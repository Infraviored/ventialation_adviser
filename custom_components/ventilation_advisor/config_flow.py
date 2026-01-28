"""Adds config flow for Ventilation Advisor."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import area_registry as ar, selector

from .const import (
    CO2_CRITICAL,
    CO2_WARN,
    CONF_AREA_ID,
    CONF_CEILING_HEIGHT,
    CONF_CO2_CRITICAL_OVERRIDE,
    CONF_CO2_SENSOR,
    CONF_CO2_WARN_OVERRIDE,
    CONF_FLOOR_AREA,
    CONF_HAS_SLOPE,
    CONF_INDOOR_HUMIDITY,
    CONF_INDOOR_TEMP,
    CONF_MOULD_CRITICAL_OVERRIDE,
    CONF_MOULD_SAFE_OVERRIDE,
    CONF_OUTDOOR_HUMIDITY,
    CONF_OUTDOOR_TEMP,
    CONF_ROOM_NAME,
    CONF_ROOMS,
    CONF_SLOPE_A,
    CONF_SLOPE_B,
    CONF_SLOPE_C,
    CONF_STRATEGY,
    DEFAULT_CEILING_HEIGHT,
    DEFAULT_STRATEGY,
    DOMAIN,
    MOULD_RISK_CRITICAL,
    MOULD_RISK_SAFE,
    STRATEGY_OPTIONS,
)


class VentilationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Ventilation Advisor."""

    VERSION = 3

    async def async_step_user(self, user_input=None):
        """Handle the initial setup (System Hub)."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Ventilation System", data=user_input, options={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_OUTDOOR_TEMP): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                    ),
                    vol.Required(CONF_OUTDOOR_HUMIDITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="humidity")
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return VentilationOptionsFlowHandler(config_entry)


class VentilationOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow (Room Management)."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.entry = config_entry
        self._rooms = list(config_entry.options.get(CONF_ROOMS, []))
        self._current_room_index = None
        self._temp_room_data = {}

    async def async_step_init(self, user_input=None):
        """Manage rooms."""
        menu_options = ["add_room"]
        if self._rooms:
            menu_options.extend(["edit_room", "remove_room"])
        menu_options.append("system_config")

        return self.async_show_menu(
            step_id="init",
            menu_options=menu_options,
        )

    async def _update_system_data(self, user_input):
        """Helper to update both data and options for system-wide keys."""
        new_data = {**self.entry.data}
        new_options = {**self.entry.options}

        for key in [CONF_OUTDOOR_TEMP, CONF_OUTDOOR_HUMIDITY]:
            if key in user_input:
                new_data[key] = user_input[key]

        if CONF_STRATEGY in user_input:
            new_options[CONF_STRATEGY] = user_input[CONF_STRATEGY]

        self.hass.config_entries.async_update_entry(self.entry, data=new_data, options=new_options)
        return self.async_create_entry(title="", data=new_options)

    async def async_step_system_config(self, user_input=None):
        """Update system-wide settings."""
        if user_input is not None:
            return await self._update_system_data(user_input)

        return self.async_show_form(
            step_id="system_config",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_OUTDOOR_TEMP,
                        default=self.entry.data.get(CONF_OUTDOOR_TEMP),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                    ),
                    vol.Required(
                        CONF_OUTDOOR_HUMIDITY,
                        default=self.entry.data.get(CONF_OUTDOOR_HUMIDITY),
                    ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor", device_class="humidity")),
                    vol.Required(
                        CONF_STRATEGY,
                        default=self.entry.options.get(CONF_STRATEGY, DEFAULT_STRATEGY),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=STRATEGY_OPTIONS,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_add_room(self, user_input=None):
        """Add a new room - Start with Name and Area."""
        self._current_room_index = None
        self._temp_room_data = {}
        return await self.async_step_room_base()

    async def async_step_edit_room(self, user_input=None):
        """Choose a room to edit."""
        if user_input is not None:
            room_name = user_input["room_to_edit"]
            for i, room in enumerate(self._rooms):
                if room[CONF_ROOM_NAME] == room_name:
                    self._current_room_index = i
                    self._temp_room_data = room.copy()
                    break
            return await self.async_step_room_base()

        room_names = [r[CONF_ROOM_NAME] for r in self._rooms]
        if not room_names:
            return self.async_abort(reason="no_rooms")

        return self.async_show_form(
            step_id="edit_room",
            data_schema=vol.Schema({vol.Required("room_to_edit"): vol.In(room_names)}),
        )

    async def async_step_room_base(self, user_input=None):
        """Step 1: Room Name and Area."""
        if user_input is not None:
            # If area is selected but no name given, try to use area name
            if user_input.get(CONF_AREA_ID) and not user_input.get(CONF_ROOM_NAME):
                registry = ar.async_get(self.hass)
                area = registry.async_get_area(user_input[CONF_AREA_ID])
                if area:
                    user_input[CONF_ROOM_NAME] = area.name

            if not user_input.get(CONF_ROOM_NAME):
                return self.async_show_form(
                    step_id="room_base",
                    data_schema=self._get_room_base_schema(user_input),
                    errors={"base": "name_required"},
                )

            self._temp_room_data.update(user_input)
            if user_input.get(CONF_HAS_SLOPE):
                return await self.async_step_room_slope()
            return await self.async_step_room_sensors()

        return self.async_show_form(
            step_id="room_base",
            data_schema=self._get_room_base_schema(self._temp_room_data),
        )

    def _get_room_base_schema(self, defaults):
        return vol.Schema(
            {
                vol.Optional(CONF_ROOM_NAME, default=defaults.get(CONF_ROOM_NAME, "")): str,
                vol.Optional(CONF_AREA_ID, default=defaults.get(CONF_AREA_ID)): selector.AreaSelector(),
                vol.Required(
                    CONF_FLOOR_AREA,
                    default=defaults.get(CONF_FLOOR_AREA, 20.0),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=1000, step=0.1, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="m²"
                    )
                ),
                vol.Required(
                    CONF_CEILING_HEIGHT,
                    default=defaults.get(CONF_CEILING_HEIGHT, DEFAULT_CEILING_HEIGHT),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=10, step=0.1, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="m"
                    )
                ),
                vol.Optional(CONF_HAS_SLOPE, default=defaults.get(CONF_HAS_SLOPE, False)): bool,
            }
        )

    async def async_step_room_slope(self, user_input=None):
        """Optional step: Define sloping roof dimensions."""
        if user_input is not None:
            self._temp_room_data.update(user_input)
            return await self.async_step_room_sensors()

        def slope_selector():
            return selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.1, max=100, step=0.1, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="m"
                )
            )

        return self.async_show_form(
            step_id="room_slope",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SLOPE_A, default=self._temp_room_data.get(CONF_SLOPE_A, 1.0)): slope_selector(),
                    vol.Required(CONF_SLOPE_B, default=self._temp_room_data.get(CONF_SLOPE_B, 1.0)): slope_selector(),
                    vol.Required(CONF_SLOPE_C, default=self._temp_room_data.get(CONF_SLOPE_C, 1.0)): slope_selector(),
                }
            ),
        )

    async def async_step_room_sensors(self, user_input=None):
        """Step 2: Sensors (filtered by area if possible)."""
        if user_input is not None:
            self._temp_room_data.update(user_input)
            return await self.async_step_room_advanced()

        area_id = self._temp_room_data.get(CONF_AREA_ID)

        def filtered_selector(domain, device_class):
            config = {"domain": domain, "device_class": device_class}
            if area_id:
                config["area"] = area_id
            return selector.EntitySelector(selector.EntitySelectorConfig(**config))

        return self.async_show_form(
            step_id="room_sensors",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INDOOR_TEMP,
                        default=self._temp_room_data.get(CONF_INDOOR_TEMP),
                    ): filtered_selector("sensor", "temperature"),
                    vol.Required(
                        CONF_INDOOR_HUMIDITY,
                        default=self._temp_room_data.get(CONF_INDOOR_HUMIDITY),
                    ): filtered_selector("sensor", "humidity"),
                    vol.Optional(
                        CONF_CO2_SENSOR,
                        default=self._temp_room_data.get(CONF_CO2_SENSOR),
                    ): filtered_selector("sensor", "carbon_dioxide"),
                }
            ),
        )

    async def async_step_room_advanced(self, user_input=None):
        """Step 3: Advanced Overrides (Strategy, Thresholds)."""
        if user_input is not None:
            self._temp_room_data.update(user_input)

            if self._current_room_index is not None:
                self._rooms[self._current_room_index] = self._temp_room_data
            else:
                self._temp_room_data["id"] = str(len(self._rooms))
                self._rooms.append(self._temp_room_data)

            return await self._update_rooms()

        def num_selector(unit):
            return selector.NumberSelector(
                selector.NumberSelectorConfig(mode=selector.NumberSelectorMode.BOX, unit_of_measurement=unit)
            )

        return self.async_show_form(
            step_id="room_advanced",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_STRATEGY,
                        default=self._temp_room_data.get(CONF_STRATEGY, DEFAULT_STRATEGY),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=STRATEGY_OPTIONS,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_MOULD_SAFE_OVERRIDE,
                        default=self._temp_room_data.get(CONF_MOULD_SAFE_OVERRIDE, MOULD_RISK_SAFE),
                    ): num_selector("%"),
                    vol.Optional(
                        CONF_MOULD_CRITICAL_OVERRIDE,
                        default=self._temp_room_data.get(CONF_MOULD_CRITICAL_OVERRIDE, MOULD_RISK_CRITICAL),
                    ): num_selector("%"),
                    vol.Optional(
                        CONF_CO2_WARN_OVERRIDE,
                        default=self._temp_room_data.get(CONF_CO2_WARN_OVERRIDE, CO2_WARN),
                    ): num_selector("ppm"),
                    vol.Optional(
                        CONF_CO2_CRITICAL_OVERRIDE,
                        default=self._temp_room_data.get(CONF_CO2_CRITICAL_OVERRIDE, CO2_CRITICAL),
                    ): num_selector("ppm"),
                }
            ),
        )

    async def async_step_remove_room(self, user_input=None):
        """Remove a room."""
        if user_input is not None:
            room_name = user_input["room_to_remove"]
            self._rooms = [r for r in self._rooms if r[CONF_ROOM_NAME] != room_name]
            return await self._update_rooms()

        room_names = [r[CONF_ROOM_NAME] for r in self._rooms]
        if not room_names:
            return self.async_abort(reason="no_rooms_to_remove")

        return self.async_show_form(
            step_id="remove_room",
            data_schema=vol.Schema({vol.Required("room_to_remove"): vol.In(room_names)}),
        )

    async def _update_rooms(self):
        """Update the config entry options."""
        return self.async_create_entry(title="", data={**self.entry.options, CONF_ROOMS: self._rooms})

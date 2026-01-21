"""Adds config flow for Ventilation Advisor."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_OUTDOOR_TEMP,
    CONF_OUTDOOR_HUMIDITY,
    CONF_ROOMS,
    CONF_ROOM_NAME,
    CONF_INDOOR_TEMP,
    CONF_INDOOR_HUMIDITY,
    CONF_FLOOR_AREA,
    CONF_CEILING_HEIGHT,
    CONF_CO2_SENSOR,
    DEFAULT_CEILING_HEIGHT,
    CONF_STRATEGY,
    DEFAULT_STRATEGY,
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
            return self.async_create_entry(
                title="Ventilation System", data=user_input, options={}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_OUTDOOR_TEMP): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor", device_class="temperature"
                        )
                    ),
                    vol.Required(CONF_OUTDOOR_HUMIDITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor", device_class="humidity"
                        )
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VentilationOptionsFlowHandler(config_entry)


class VentilationOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow (Room Management)."""

    def __init__(self, config_entry):
        self._rooms = list(config_entry.options.get(CONF_ROOMS, []))

    async def async_step_init(self, user_input=None):
        """Manage rooms."""
        return self.async_show_menu(
            step_id="init", menu_options=["add_room", "remove_room", "system_config"]
        )

    async def async_step_system_config(self, user_input=None):
        """Update system-wide settings."""
        if user_input is not None:
            new_data = {**self.config_entry.data, **user_input}
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data=self.config_entry.options)

        return self.async_show_form(
            step_id="system_config",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_OUTDOOR_TEMP,
                        default=self.config_entry.data.get(CONF_OUTDOOR_TEMP),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor", device_class="temperature"
                        )
                    ),
                    vol.Required(
                        CONF_OUTDOOR_HUMIDITY,
                        default=self.config_entry.data.get(CONF_OUTDOOR_HUMIDITY),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor", device_class="humidity"
                        )
                    ),
                    vol.Required(
                        CONF_STRATEGY,
                        default=self.config_entry.options.get(
                            CONF_STRATEGY, DEFAULT_STRATEGY
                        ),
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
        """Add a new room."""
        if user_input is not None:
            self._rooms.append({"id": str(len(self._rooms)), **user_input})
            return await self._update_rooms()

        return self.async_show_form(
            step_id="add_room",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ROOM_NAME): str,
                    vol.Required(CONF_INDOOR_TEMP): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor", device_class="temperature"
                        )
                    ),
                    vol.Required(CONF_INDOOR_HUMIDITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor", device_class="humidity"
                        )
                    ),
                    vol.Optional(CONF_CO2_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor", device_class="carbon_dioxide"
                        )
                    ),
                    vol.Required(CONF_FLOOR_AREA): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=1000,
                            step=0.1,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="m²",
                        )
                    ),
                    vol.Required(
                        CONF_CEILING_HEIGHT, default=DEFAULT_CEILING_HEIGHT
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=10,
                            step=0.1,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="m",
                        )
                    ),
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
            data_schema=vol.Schema(
                {vol.Required("room_to_remove"): vol.In(room_names)}
            ),
        )

    async def _update_rooms(self):
        """Update the config entry options."""
        return self.async_create_entry(
            title="", data={**self.config_entry.options, CONF_ROOMS: self._rooms}
        )

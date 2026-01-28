"""Sensor platform for Ventilation Advisor."""

from __future__ import annotations

import math

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

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
    DEFAULT_STRATEGY,
    DOMAIN,
    MAGNUS_A,
    MAGNUS_B,
    MAGNUS_C,
    MAGNUS_K,
    MOULD_RISK_CRITICAL,
    MOULD_RISK_SAFE,
    STRATEGY_AGGRESSIVE,
    STRATEGY_ENERGY_SAVER,
    STRATEGY_FRESH_AIR,
)


def calculate_absolute_humidity(temperature: float, humidity: float) -> float:
    """Calculate absolute humidity in g/m³ using the Magnus Formula."""
    t = temperature
    rh = humidity

    # Saturation Vapor Pressure (hPa)
    if (t + MAGNUS_C) == 0:
        return 0.0

    p_sat = MAGNUS_A * math.exp((MAGNUS_B * t) / (t + MAGNUS_C))

    # Actual Vapor Pressure (hPa)
    p_act = p_sat * (rh / 100.0)

    # Absolute Humidity (g/m³)
    ah = 216.7 * (p_act / (MAGNUS_K + t))

    return round(ah, 2)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    rooms = entry.options.get(CONF_ROOMS, [])
    entities = []

    entities.append(GlobalOutdoorAHSensor(entry))

    for room in rooms:
        entities.extend(
            [
                WaterContentSensor(entry, room),
                IndoorAHSensor(entry, room),
                MouldRiskSensor(entry, room),
                DryingPotentialSensor(entry, room),
                VentilationEfficiencySensor(entry, room),
                MasterAdviceSensor(entry, room),
                RoomVolumeSensor(entry, room),
            ]
        )

    async_add_entities(entities)


class VentilationSensorBase(SensorEntity):
    """Base class with common logic."""

    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, room: dict | None = None):
        """Initialize the sensor."""
        self._entry = entry
        self._room = room
        if room:
            self._room_id = room.get("id", room[CONF_ROOM_NAME])

    async def async_added_to_hass(self):
        """Register callbacks."""
        entity_ids = self._get_listening_entities()
        self.async_on_remove(async_track_state_change_event(self.hass, entity_ids, self._async_update_event))
        self._async_update_event()

    @property
    def device_info(self):
        """Return device information."""
        if not self._room:
            return None

        # Group all sensors for this room into one device
        info = {
            "identifiers": {(DOMAIN, self._room_id)},
            "name": self._room[CONF_ROOM_NAME],
            "manufacturer": "Ventilation Advisor",
            "model": "Room Advisor",
        }

        # If the user selected an area, link the device to it
        if area_id := self._room.get(CONF_AREA_ID):
            info["suggested_area"] = area_id

        return info

    @callback
    def _async_update_event(self, event=None):
        self.async_schedule_update_ha_state(True)

    def _get_listening_entities(self):
        ids = [
            self._entry.data[CONF_OUTDOOR_TEMP],
            self._entry.data[CONF_OUTDOOR_HUMIDITY],
        ]
        if room := self._room:
            ids.extend([room[CONF_INDOOR_TEMP], room[CONF_INDOOR_HUMIDITY]])
            if room.get(CONF_CO2_SENSOR):
                ids.append(room[CONF_CO2_SENSOR])
        return ids

    def _get_float_state(self, entity_id):
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state and state.state not in ("unknown", "unavailable"):
            try:
                return float(state.state)
            except ValueError:
                pass
        return None


class GlobalOutdoorAHSensor(VentilationSensorBase):
    """Global Outdoor AH."""

    _attr_icon = "mdi:water"
    _attr_native_unit_of_measurement = "g/m³"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry):
        """Initialize outdoor humidity sensor."""
        super().__init__(entry)
        self._attr_name = "Outdoor Absolute Humidity"
        self._attr_unique_id = f"{entry.entry_id}_global_outdoor_ah"

    @property
    def device_info(self):
        """Return system device info."""
        return {
            "identifiers": {(DOMAIN, "system")},
            "name": "Ventilation System",
            "manufacturer": "Ventilation Advisor",
            "entry_type": "service",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        t = self._get_float_state(self._entry.data[CONF_OUTDOOR_TEMP])
        h = self._get_float_state(self._entry.data[CONF_OUTDOOR_HUMIDITY])
        return calculate_absolute_humidity(t, h) if t is not None and h is not None else None


class IndoorAHSensor(VentilationSensorBase):
    """Room AH."""

    _attr_icon = "mdi:water"
    _attr_native_unit_of_measurement = "g/m³"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, room: dict):
        """Initialize indoor humidity sensor."""
        super().__init__(entry, room)
        self._attr_name = f"{room[CONF_ROOM_NAME]} Absolute Humidity"
        self._attr_unique_id = f"{entry.entry_id}_{self._room_id}_indoor_ah"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not (room := self._room):
            return None
        t = self._get_float_state(room[CONF_INDOOR_TEMP])
        h = self._get_float_state(room[CONF_INDOOR_HUMIDITY])
        return calculate_absolute_humidity(t, h) if t is not None and h is not None else None


class WaterContentSensor(VentilationSensorBase):
    """Room Water Content (ml)."""

    _attr_icon = "mdi:water-percent"
    _attr_native_unit_of_measurement = "ml"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, room: dict):
        """Initialize water content sensor."""
        super().__init__(entry, room)
        self._attr_name = f"{room[CONF_ROOM_NAME]} Water Content"
        self._attr_unique_id = f"{entry.entry_id}_{self._room_id}_water_ml"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not (room := self._room):
            return None
        t = self._get_float_state(room[CONF_INDOOR_TEMP])
        h = self._get_float_state(room[CONF_INDOOR_HUMIDITY])
        if t is not None and h is not None:
            ah = calculate_absolute_humidity(t, h)
            volume = room[CONF_FLOOR_AREA] * room[CONF_CEILING_HEIGHT]

            # Substract sloping roof volume if configured
            if room.get(CONF_HAS_SLOPE):
                v_slope = 0.5 * room.get(CONF_SLOPE_A, 0) * room.get(CONF_SLOPE_B, 0) * room.get(CONF_SLOPE_C, 0)
                volume = max(0, volume - v_slope)

            return round(ah * volume, 1)
        return None


class MouldRiskSensor(VentilationSensorBase):
    """Mould Risk 0-100%."""

    _attr_icon = "mdi:alert-octagon"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, room: dict):
        """Initialize mould risk sensor."""
        super().__init__(entry, room)
        self._attr_name = f"{room[CONF_ROOM_NAME]} Mould Risk"
        self._attr_unique_id = f"{entry.entry_id}_{self._room_id}_mould_risk"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not (room := self._room):
            return None
        rh = self._get_float_state(room[CONF_INDOOR_HUMIDITY])
        if rh is None:
            return None

        safe = room.get(CONF_MOULD_SAFE_OVERRIDE, MOULD_RISK_SAFE)
        critical = room.get(CONF_MOULD_CRITICAL_OVERRIDE, MOULD_RISK_CRITICAL)

        if rh < safe:
            return 0.0
        if rh >= critical:
            return 100.0

        score = (rh - safe) * (100 / (critical - safe))
        return round(score, 0)


class DryingPotentialSensor(VentilationSensorBase):
    """Drying Potential (AH Delta g/m³)."""

    _attr_icon = "mdi:weather-windy"
    _attr_native_unit_of_measurement = "g/m³"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, room: dict):
        """Initialize drying potential sensor."""
        super().__init__(entry, room)
        self._attr_name = f"{room[CONF_ROOM_NAME]} Drying Potential"
        self._attr_unique_id = f"{entry.entry_id}_{self._room_id}_drying_power"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not (room := self._room):
            return None
        i_t = self._get_float_state(room[CONF_INDOOR_TEMP])
        i_h = self._get_float_state(room[CONF_INDOOR_HUMIDITY])
        o_t = self._get_float_state(self._entry.data[CONF_OUTDOOR_TEMP])
        o_h = self._get_float_state(self._entry.data[CONF_OUTDOOR_HUMIDITY])
        if i_t is None or i_h is None or o_t is None or o_h is None:
            return None
        i_ah = calculate_absolute_humidity(i_t, i_h)
        o_ah = calculate_absolute_humidity(o_t, o_h)
        return round(i_ah - o_ah, 2)


class VentilationEfficiencySensor(VentilationSensorBase):
    """Ventilation Efficiency."""

    _attr_icon = "mdi:leaf"

    def __init__(self, entry: ConfigEntry, room: dict):
        """Initialize ventilation efficiency sensor."""
        super().__init__(entry, room)
        self._attr_name = f"{room[CONF_ROOM_NAME]} Ventilation Efficiency"
        self._attr_unique_id = f"{entry.entry_id}_{self._room_id}_efficiency"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not (room := self._room):
            return "Unknown"
        i_t = self._get_float_state(room[CONF_INDOOR_TEMP])
        o_t = self._get_float_state(self._entry.data[CONF_OUTDOOR_TEMP])
        i_h = self._get_float_state(room[CONF_INDOOR_HUMIDITY])
        o_h = self._get_float_state(self._entry.data[CONF_OUTDOOR_HUMIDITY])

        if i_t is None or o_t is None or i_h is None or o_h is None:
            return "Unknown"

        dp = calculate_absolute_humidity(i_t, i_h) - calculate_absolute_humidity(o_t, o_h)
        if dp <= 0:
            return "Counter-Productive"

        dt = i_t - o_t
        if dt <= 0:
            return "High (Free Cooling)"

        penalty_factor = 1.0
        if i_h > 40:
            penalty_factor = 1 + ((i_h - 40) * 0.005)

        effective_cost = dt * penalty_factor
        ratio = dp / effective_cost
        if ratio > 0.3:
            return "High"
        if ratio > 0.1:
            return "Medium"
        return "Low (Wasteful)"


class MasterAdviceSensor(VentilationSensorBase):
    """Master Advice."""

    _attr_icon = "mdi:window-open-variant"

    def __init__(self, entry: ConfigEntry, room: dict):
        """Initialize master advice sensor."""
        super().__init__(entry, room)
        self._attr_name = f"{room[CONF_ROOM_NAME]} Master Advice"
        self._attr_unique_id = f"{entry.entry_id}_{self._room_id}_master_advice"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not (room := self._room):
            return "Unknown"

        risk_sensor = MouldRiskSensor(self._entry, room)
        risk_sensor.hass = self.hass
        risk_val = risk_sensor.native_value

        power_sensor = DryingPotentialSensor(self._entry, room)
        power_sensor.hass = self.hass
        power_val = power_sensor.native_value

        eff_sensor = VentilationEfficiencySensor(self._entry, room)
        eff_sensor.hass = self.hass
        eff_val = eff_sensor.native_value

        co2_val = self._get_float_state(room.get(CONF_CO2_SENSOR))

        if risk_val is None or power_val is None or eff_val == "Unknown" or eff_val is None:
            return "Unknown"

        # Overrides
        c_warn = room.get(CONF_CO2_WARN_OVERRIDE, CO2_WARN)
        c_crit = room.get(CONF_CO2_CRITICAL_OVERRIDE, CO2_CRITICAL)

        if risk_val >= 80:
            return "Urgent (Mould Risk)"

        if co2_val is not None and co2_val >= c_crit:
            return "Urgent (Air Quality)"

        if power_val <= 0:
            if co2_val and co2_val >= c_warn:
                return "Recommended (Fresh Air)"
            return "Hold (Ineffective)"

        strategy = room.get(CONF_STRATEGY, self._entry.options.get(CONF_STRATEGY, DEFAULT_STRATEGY))

        if strategy == STRATEGY_ENERGY_SAVER:
            if eff_val.startswith("High"):
                return "Optional (Efficient)"
            return "Hold (Eco Mode)"

        if strategy == STRATEGY_AGGRESSIVE:
            return "Recommended (Drying)"

        is_fresh_air_lover = strategy == STRATEGY_FRESH_AIR
        if risk_val > (30 if is_fresh_air_lover else 50):
            return "Recommended"
        if power_val > (1.0 if is_fresh_air_lover else 2.0):
            return "Recommended (Quick)"
        if eff_val.startswith("High"):
            return "Optional (Efficient)"

        return "Hold (Low Necessity)"


class RoomVolumeSensor(VentilationSensorBase):
    """Room Volume (Diagnostic)."""

    _attr_icon = "mdi:cube-outline"
    _attr_native_unit_of_measurement = "m³"
    _attr_entity_category = "diagnostic"

    def __init__(self, entry: ConfigEntry, room: dict):
        """Initialize."""
        super().__init__(entry, room)
        self._attr_name = f"{room[CONF_ROOM_NAME]} Calculated Volume"
        self._attr_unique_id = f"{entry.entry_id}_{self._room_id}_volume"

    @property
    def native_value(self):
        """Return volume."""
        if not (room := self._room):
            return None
        volume = room[CONF_FLOOR_AREA] * room[CONF_CEILING_HEIGHT]
        if room.get(CONF_HAS_SLOPE):
            v_slope = 0.5 * room.get(CONF_SLOPE_A, 0) * room.get(CONF_SLOPE_B, 0) * room.get(CONF_SLOPE_C, 0)
            volume = max(0, volume - v_slope)
        return round(volume, 2)

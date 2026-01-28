"""Select platform for Ventilation Advisor."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ROOMS, CONF_STRATEGY, DEFAULT_STRATEGY, DOMAIN, STRATEGY_OPTIONS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    entities: list[SelectEntity] = []

    # Global strategy
    entities.append(VentilationStrategySelect(entry))

    # Per-room strategy
    rooms = entry.options.get(CONF_ROOMS, [])
    entities.extend(RoomStrategySelect(entry, room) for room in rooms)

    async_add_entities(entities)


class VentilationStrategySelect(SelectEntity):
    """Select entity for Global Ventilation Strategy."""

    _attr_icon = "mdi:tune"
    _attr_options = STRATEGY_OPTIONS

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize."""
        self._entry = entry
        self._attr_name = "Global Suggestion Frequency"
        self._attr_unique_id = f"{entry.entry_id}_global_strategy"

    @property
    def device_info(self):
        """Return system device info."""
        return {
            "identifiers": {(DOMAIN, "system")},
            "name": "Ventilation System",
            "manufacturer": "Ventilation Advisor",
        }

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option."""
        return self._entry.options.get(CONF_STRATEGY, DEFAULT_STRATEGY)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        options = {**self._entry.options, CONF_STRATEGY: option}
        self.hass.config_entries.async_update_entry(self._entry, options=options)


class RoomStrategySelect(SelectEntity):
    """Select entity for Room-Specific Ventilation Strategy."""

    _attr_icon = "mdi:tune"
    _attr_options = STRATEGY_OPTIONS

    def __init__(self, entry: ConfigEntry, room: dict) -> None:
        """Initialize."""
        self._entry = entry
        self._room = room
        self._room_id = room.get("id", room["name"])
        self._attr_name = f"{room['name']} Suggestion Frequency"
        self._attr_unique_id = f"{entry.entry_id}_{self._room_id}_strategy"

    @property
    def device_info(self):
        """Link to room device."""
        return {
            "identifiers": {(DOMAIN, self._room_id)},
            "name": self._room["name"],
            "manufacturer": "Ventilation Advisor",
            "model": "Room Advisor",
        }

    @property
    def current_option(self) -> str | None:
        """Return the room strategy or global fallback."""
        return self._room.get(CONF_STRATEGY, self._entry.options.get(CONF_STRATEGY, DEFAULT_STRATEGY))

    async def async_select_option(self, option: str) -> None:
        """Change the room strategy."""
        rooms = list(self._entry.options.get(CONF_ROOMS, []))
        for room in rooms:
            if room.get("id", room["name"]) == self._room_id:
                room[CONF_STRATEGY] = option
                break

        options = {**self._entry.options, CONF_ROOMS: rooms}
        self.hass.config_entries.async_update_entry(self._entry, options=options)

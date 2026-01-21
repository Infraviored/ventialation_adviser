"""Select platform for Ventilation Advisor."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_STRATEGY,
    DEFAULT_STRATEGY,
    STRATEGY_OPTIONS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    # We only have one global strategy selector
    async_add_entities([VentilationStrategySelect(entry)])


class VentilationStrategySelect(SelectEntity):
    """Select entity for Ventilation Strategy."""

    _attr_icon = "mdi:tune"
    _attr_options = STRATEGY_OPTIONS

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize."""
        self._entry = entry
        self._attr_name = "Suggestion Frequency"
        self._attr_unique_id = f"{entry.entry_id}_strategy"

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self._entry.options.get(CONF_STRATEGY, DEFAULT_STRATEGY)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        hass = self.hass
        data = {**self._entry.options, CONF_STRATEGY: option}
        hass.config_entries.async_update_entry(self._entry, options=data)

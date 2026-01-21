"""Custom types for ventilation_advisor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import VentilationAdvisorApiClient
    from .coordinator import VentilationAdvisorDataUpdateCoordinator


type VentilationAdvisorConfigEntry = ConfigEntry[VentilationAdvisorData]


@dataclass
class VentilationAdvisorData:
    """Data for ventilation_advisor."""

    client: VentilationAdvisorApiClient
    coordinator: VentilationAdvisorDataUpdateCoordinator
    integration: Integration

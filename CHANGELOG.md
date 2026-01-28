# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-28

### Added

- **Per-Room Strategy Control**: Every room now acts as an independent climate zone. You can assign different suggestion priorities—for example, setting a "Bathroom" to Aggressive drying while keeping "Bedrooms" on Energy Saver.
- **Advanced Threshold Overrides**: Full control over health and safety limits per room. Customize the specific humidity percentages for Mould Risk (Safe/Critical) and define unique CO2 warning levels (ppm) for sensitive areas.
- **Architectural Volume Correction**: Introduced a geometric tool for rooms with sloping roofs. By defining the dimensions of subtractive triangular prisms (Width, Height, Length), the integration calculates the precise effective volume for moisture tracking.
- **Smart Area Integration**:
  - Direct linking to Home Assistant Areas.
  - Automatic pre-filling of room names based on the selected area.
  - Adaptive sensor filtering that only suggests temperature, humidity, and CO2 sensors already assigned to the chosen area.
- **System Diagnostics**: Added a calculated volume entity (marked as Diagnostic) to provide transparency into how the room geometry is being processed.
- **Official Identity**: Fully developed branding assets including high-resolution icons (256px and 512px) and logos to ensure a premium appearance in the Home Assistant UI.

### Fixed

- **Persistent Configuration Management**: Rooms can now be edited or refined after initial setup without needing to be deleted and recreated.
- **Native Device Grouping**: Sensors are no longer listed as isolated entities. They are now logically grouped under a single "Room Device," which properly handles area assignments and provides a cleaner "Devices" view.
- **UI Organization**: Global settings and system-wide outdoor sensors are now isolated into a designated "Ventilation System" device to prevent clutter in individual room dashboards.

## [1.0.0] - 2026-01-22

### Added

- Initial release of Ventilation Advisor.
- Real-time Indoor/Outdoor Absolute Humidity calculations using physics-based formulas.
- Core sensors for Mould Risk probability and Drying Potential.
- Central strategy management for standardizing ventilation advice across the home.

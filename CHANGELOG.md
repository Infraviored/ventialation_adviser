# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-01-28

### Fixed

- **Critical Data Entry Crash**: Fixed a conflict where the integration was trying to overwrite a read-only property in the Home Assistant core. This was the primary cause of the "500 Internal Server Error" during configuration.

## [1.1.0] - 2026-01-28

### Added

- **Per-Room Strategy Control**: Every room now acts as an independent climate zone. You can assign different suggestion priorities—for example, setting a "Bathroom" to Aggressive drying while keeping "Bedrooms" on Energy Saver.
- **Advanced Threshold Overrides**: Full control over health and safety limits per room. Customize the specific humidity percentages for Mould Risk (Safe/Critical) and define unique CO2 warning levels (ppm) for sensitive areas.
- **Architectural Volume Correction**: Introduced a geometric tool for rooms with sloping roofs. By defining the dimensions of subtractive triangular prisms (Width, Height, Length), the integration calculates the precise effective volume for moisture tracking.
- **Smart Area Integration**:
  - Direct linking to Home Assistant Areas.
  - Automatic pre-filling of room names based on the selected area.
  - Adaptive sensor filtering that only suggests temperature, humidity, and CO2 sensors already assigned to the chosen area.
- **System Diagnostics**: Added a downloadable diagnostics tool and a calculated volume entity to provide transparency into the system's internal state and geometry math.
- **Official Identity**: Fully developed branding assets including high-resolution icons (256px and 512px) and logos to ensure a premium appearance in the Home Assistant UI.

### Fixed

- **System Stability**: Resolved a critical 500 error in the configuration flow that occurred when updating system-wide settings.
- **Area Assignment Logic**: The main Ventilation System is now correctly identified as a service hub, preventing Home Assistant from inappropriately asking to assign it to a specific room during initial setup.
- **Persistent Configuration Management**: Rooms can now be edited or refined after initial setup without needing to be deleted and recreated.
- **Native Device Grouping**: Sensors are now logically grouped under a single "Room Device," providing a cleaner "Devices" view and better organization.
- **UI Organization**: Global settings and outdoor sensors are isolated into a designated "Ventilation System" device to prevent clutter in individual room dashboards.

## [1.0.0] - 2026-01-22

### Added

- Initial release of Ventilation Advisor.
- Real-time Indoor/Outdoor Absolute Humidity calculations using physics-based formulas.
- Core sensors for Mould Risk probability and Drying Potential.
- Central strategy management for standardizing ventilation advice across the home.

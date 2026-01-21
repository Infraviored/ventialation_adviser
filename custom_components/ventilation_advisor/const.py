"""Constants for ventilation_advisor."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "ventilation_advisor"

# Configuration Keys
CONF_OUTDOOR_TEMP = "outdoor_temp"
CONF_OUTDOOR_HUMIDITY = "outdoor_humidity"
CONF_STRATEGY = "strategy"
CONF_ROOMS = "rooms"
CONF_ROOM_NAME = "name"
CONF_INDOOR_TEMP = "temp_sensor"
CONF_INDOOR_HUMIDITY = "humidity_sensor"
CONF_FLOOR_AREA = "floor_area"
CONF_CEILING_HEIGHT = "ceiling_height"
CONF_CO2_SENSOR = "co2_sensor"

# Defaults
DEFAULT_CEILING_HEIGHT = 2.8
DEFAULT_STRATEGY = "Balanced"

# Strategy Options
STRATEGY_ENERGY_SAVER = "Energy Saver"
STRATEGY_BALANCED_ECO = "Balanced (Eco)"
STRATEGY_BALANCED = "Balanced"
STRATEGY_FRESH_AIR = "Fresh Air Lover"
STRATEGY_AGGRESSIVE = "Aggressive"

STRATEGY_OPTIONS = [
    STRATEGY_ENERGY_SAVER,
    STRATEGY_BALANCED_ECO,
    STRATEGY_BALANCED,
    STRATEGY_FRESH_AIR,
    STRATEGY_AGGRESSIVE,
]

# Strategy Thresholds (Scaling factor for Efficiency logic)
STRATEGY_THRESHOLDS = {
    STRATEGY_ENERGY_SAVER: 85,
    STRATEGY_BALANCED_ECO: 65,
    STRATEGY_BALANCED: 45,
    STRATEGY_FRESH_AIR: 25,
    STRATEGY_AGGRESSIVE: 5,
}

# Physics Constants (Magnus Formula)
MAGNUS_K = 273.15
MAGNUS_A = 6.112
MAGNUS_B = 17.67
MAGNUS_C = 243.5

# Thresholds
MOULD_RISK_SAFE = 55
MOULD_RISK_CRITICAL = 80
CO2_WARN = 1000
CO2_CRITICAL = 1500

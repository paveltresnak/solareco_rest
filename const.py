"""Constants for SolarEco REST integration."""

DOMAIN = "solareco_rest"
CONF_DEVICE_ID = "device_id"
DEFAULT_SCAN_INTERVAL = 30

# Sensor definitions
SENSORS = {
    "919": {
        "name": "Voltage",
        "key": "voltage",
        "unit": "V",
        "device_class": "voltage",
        "state_class": "measurement",
        "icon": "mdi:lightning-bolt",
        "transform": lambda x: float(x),
    },
    "920": {
        "name": "Current",
        "key": "current",
        "unit": "A",
        "device_class": "current",
        "state_class": "measurement",
        "icon": "mdi:current-dc",
        "transform": lambda x: float(x) / 1000,  # mA to A
    },
    "921": {
        "name": "Power",
        "key": "power",
        "unit": "W",
        "device_class": "power",
        "state_class": "measurement",
        "icon": "mdi:flash",
        "transform": lambda x: float(x),
    },
    "923": {
        "name": "Temperature",
        "key": "temperature",
        "unit": "\u00b0C",
        "device_class": "temperature",
        "state_class": "measurement",
        "icon": "mdi:thermometer",
        "transform": lambda x: float(x),
    },
    "924": {
        "name": "Daily Production",
        "key": "daily_production",
        "unit": "Wh",
        "device_class": "energy",
        "state_class": "total_increasing",
        "icon": "mdi:solar-power",
        "transform": lambda x: float(x),
    },

}

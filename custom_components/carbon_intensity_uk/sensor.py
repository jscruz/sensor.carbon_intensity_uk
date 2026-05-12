"""Sensor platform for carbon intensity UK."""
import logging

from custom_components.carbon_intensity_uk.const import (
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    HIGH_ICON,
    LOW_ICON,
    MODERATE_ICON,
)
from custom_components.carbon_intensity_uk.entity import CarbonIntensityEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = [
    {
        "key": "current_period_index",
        "name": f"{DEFAULT_NAME} Current Index",
        "unit": None,
        "icon": ICON,
        "dynamic_icon": True,
    },
    {
        "key": "current_period_forecast",
        "name": f"{DEFAULT_NAME} Current Intensity",
        "unit": "gCO2/kWh",
        "icon": "mdi:molecule-co2",
        "dynamic_icon": False,
    },
    {
        "key": "current_period_national_index",
        "name": f"{DEFAULT_NAME} National Index",
        "unit": None,
        "icon": ICON,
        "dynamic_icon": False,
    },
    {
        "key": "current_period_national_forecast",
        "name": f"{DEFAULT_NAME} National Intensity",
        "unit": "gCO2/kWh",
        "icon": "mdi:molecule-co2",
        "dynamic_icon": False,
    },
    {
        "key": "current_low_carbon_percentage",
        "name": f"{DEFAULT_NAME} Low Carbon Percentage",
        "unit": "%",
        "icon": "mdi:wind-turbine",
        "dynamic_icon": False,
    },
    {
        "key": "current_fossil_fuel_percentage",
        "name": f"{DEFAULT_NAME} Fossil Fuel Percentage",
        "unit": "%",
        "icon": "mdi:fire",
        "dynamic_icon": False,
    },
    {
        "key": "lowest_period_index",
        "name": f"{DEFAULT_NAME} Lowest Period Index",
        "unit": None,
        "icon": "mdi:leaf",
        "dynamic_icon": False,
    },
    {
        "key": "lowest_period_forecast",
        "name": f"{DEFAULT_NAME} Lowest Period Intensity",
        "unit": "gCO2/kWh",
        "icon": "mdi:molecule-co2",
        "dynamic_icon": False,
    },
    {
        "key": "optimal_window_index",
        "name": f"{DEFAULT_NAME} Optimal Window Index",
        "unit": None,
        "icon": "mdi:clock-check",
        "dynamic_icon": False,
    },
    {
        "key": "optimal_window_forecast",
        "name": f"{DEFAULT_NAME} Optimal Window Intensity",
        "unit": "gCO2/kWh",
        "icon": "mdi:molecule-co2",
        "dynamic_icon": False,
    },
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.error(
        "[carbon_intensity_uk] sensor async_setup_entry — coordinator data keys: %s",
        list(coordinator.data.keys()) if coordinator.data else None,
    )
    sensors = [CarbonIntensitySensor(coordinator, entry, sensor) for sensor in SENSOR_TYPES]
    _LOGGER.error("[carbon_intensity_uk] Creating %d sensors: %s", len(sensors), [s.name for s in sensors])
    async_add_devices(sensors)


class CarbonIntensitySensor(CarbonIntensityEntity):
    """Carbon Intensity Sensor class."""

    def __init__(self, coordinator, config_entry, sensor_type):
        super().__init__(coordinator, config_entry)
        self._sensor_type = sensor_type

    @property
    def name(self):
        return self._sensor_type["name"]

    @property
    def unique_id(self):
        return f"{self.config_entry.entry_id}_{self._sensor_type['key']}"

    @property
    def state(self):
        return self.coordinator.data.get(self._sensor_type["key"]) if self.coordinator.data else None

    @property
    def unit_of_measurement(self):
        return self._sensor_type.get("unit")

    @property
    def icon(self):
        if self._sensor_type["dynamic_icon"]:
            index = self.coordinator.data.get("current_period_index") if self.coordinator.data else None
            if index == "high":
                return HIGH_ICON
            elif index == "moderate":
                return MODERATE_ICON
            elif index == "low":
                return LOW_ICON
        return self._sensor_type["icon"]

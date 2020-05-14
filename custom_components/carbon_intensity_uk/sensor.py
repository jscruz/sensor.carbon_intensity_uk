"""Sensor platform for carbon intensity UK."""
from custom_components.carbon_intensity_uk.const import (
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    SENSOR,
)
from custom_components.carbon_intensity_uk.entity import CarbonIntensityEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([CarbonIntensitySensor(coordinator, entry)])


class CarbonIntensitySensor(CarbonIntensityEntity):
    """Carbon Intensity Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("current_period_index")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

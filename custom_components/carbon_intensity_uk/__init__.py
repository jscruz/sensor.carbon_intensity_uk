"""
Custom integration to integrate UK Carbon Intensity API with Home Assistant.

For more details about this integration, please refer to
https://github.com/jscruz/sensor.carbon_intensity_uk
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from carbonintensity.client import Client as CarbonIntentisityApi

from .const import (
    CONF_POSTCODE,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(seconds=600)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    postcode = entry.data.get(CONF_POSTCODE)
    _LOGGER.debug("Setting up Carbon Intensity UK for postcode: %s", postcode)

    coordinator = CarbonIntensityDataUpdateCoordinator(hass, postcode=postcode)
    _LOGGER.debug("Performing initial data fetch for postcode: %s", postcode)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        _LOGGER.warning(
            "Initial data fetch failed for postcode %s — will retry on next poll", postcode
        )
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    platforms = [p for p in PLATFORMS if entry.options.get(p, True)]
    _LOGGER.debug("Forwarding entry setup to platforms: %s", platforms)
    coordinator.platforms.extend(platforms)
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    entry.add_update_listener(async_reload_entry)
    return True


class CarbonIntensityDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, postcode):
        """Initialize."""
        self.api = CarbonIntentisityApi(postcode)
        self.platforms = []

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            _LOGGER.debug("Fetching data from Carbon Intensity API")
            data = await self.api.async_get_data()
            result = data.get("data", {})
            _LOGGER.debug(
                "Data fetch succeeded: index=%s, forecast=%s gCO2/kWh",
                result.get("current_period_index"),
                result.get("current_period_forecast"),
            )
            return result
        except Exception as exception:
            _LOGGER.warning("Failed to fetch data from Carbon Intensity API: %s", exception)
            raise UpdateFailed(exception)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    postcode = entry.data.get(CONF_POSTCODE)
    _LOGGER.debug("Unloading Carbon Intensity UK entry for postcode: %s", postcode)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("Successfully unloaded Carbon Intensity UK entry for postcode: %s", postcode)
    else:
        _LOGGER.warning("Failed to unload one or more platforms for postcode: %s", postcode)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    _LOGGER.debug("Reloading Carbon Intensity UK entry for postcode: %s", entry.data.get(CONF_POSTCODE))
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

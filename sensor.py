"""Sensor platform for SolarEco REST integration."""
from datetime import timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, CONF_DEVICE_ID, SENSORS, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SolarEco REST sensor based on a config entry."""
    device_id = config_entry.data[CONF_DEVICE_ID]
    scan_interval = config_entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    coordinator = SolarEcoDataUpdateCoordinator(
        hass,
        device_id=device_id,
        scan_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    entities = [
        SolarEcoSensor(coordinator, device_id, feed_id, sensor_config)
        for feed_id, sensor_config in SENSORS.items()
    ]

    async_add_entities(entities)


class SolarEcoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching SolarEco data from API."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_id: str,
        scan_interval: int,
    ) -> None:
        """Initialize."""
        self.device_id = device_id
        self.url = f"https://emon.solareco.cz/emoncms/{device_id}/feed/list.json"

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"HTTP {response.status}")

                    json_data = await response.json()

                    if not isinstance(json_data, list):
                        raise UpdateFailed("Invalid data format")

                    # Convert list to dict with feed ID as key
                    data = {}
                    for feed in json_data:
                        feed_id = feed.get("id")
                        if feed_id in SENSORS:
                            try:
                                raw_value = feed.get("value", 0)
                                transform = SENSORS[feed_id]["transform"]
                                data[feed_id] = {
                                    "value": transform(raw_value),
                                    "time": feed.get("time"),
                                    "name": feed.get("name"),
                                }
                            except (ValueError, TypeError) as err:
                                _LOGGER.warning(
                                    f"Failed to parse feed {feed_id}: {err}"
                                )
                                data[feed_id] = {"value": None, "time": None, "name": None}

                    return data

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")


class SolarEcoSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SolarEco sensor."""

    def __init__(
        self,
        coordinator: SolarEcoDataUpdateCoordinator,
        device_id: str,
        feed_id: str,
        config: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._feed_id = feed_id
        self._config = config
        self._device_id = device_id

        self._attr_unique_id = f"{device_id}_{config['key']}"
        self._attr_translation_key = config["key"]
        self._attr_has_entity_name = True
        self._attr_native_unit_of_measurement = config["unit"]
        self._attr_device_class = config["device_class"]
        self._attr_state_class = config["state_class"]
        self._attr_icon = config["icon"]

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self._feed_id in self.coordinator.data:
            return self.coordinator.data[self._feed_id].get("value")
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._feed_id in self.coordinator.data
        )

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"SolarEco {self._device_id[:8]}",
            "manufacturer": "SolarEco",
            "model": "MPPT Regulator",
        }
"""Config flow for SolarEco REST integration."""
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_DEVICE_ID, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_ID): str,
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=300)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    device_id = data[CONF_DEVICE_ID]
    url = f"https://emon.solareco.cz/emoncms/{device_id}/feed/list.json"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    raise CannotConnect(f"HTTP {response.status}")
                
                json_data = await response.json()
                
                if not isinstance(json_data, list) or len(json_data) == 0:
                    raise InvalidDeviceId("No data returned from API")
                
                # Check if we have expected feed IDs
                feed_ids = [feed.get("id") for feed in json_data]
                if "919" not in feed_ids or "924" not in feed_ids:
                    _LOGGER.warning(f"Expected feed IDs not found. Got: {feed_ids}")
                
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Connection error: {err}") from err
    except Exception as err:
        raise CannotConnect(f"Unknown error: {err}") from err

    return {"title": f"SolarEco {device_id[:8]}"}


class SolarEcoRestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SolarEco REST."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidDeviceId:
                errors["base"] = "invalid_device_id"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidDeviceId(HomeAssistantError):
    """Error to indicate invalid device ID."""

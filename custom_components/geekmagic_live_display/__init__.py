"""Support for displaying live Home Assistant data on GeekMagic SmallTV."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import GeekMagicClient, GeekMagicError, render_display
from .const import (
    ATTR_BACKGROUND_COLOR,
    ATTR_ENTRY_ID,
    ATTR_FOREGROUND_COLOR,
    ATTR_MESSAGE,
    ATTR_TITLE,
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_FOREGROUND_COLOR,
    DOMAIN,
    SERVICE_SHOW,
)

_LOGGER = logging.getLogger(__name__)

SERVICE_SHOW_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_TITLE, default="Home Assistant"): cv.string,
        vol.Optional(
            ATTR_FOREGROUND_COLOR, default=DEFAULT_FOREGROUND_COLOR
        ): cv.string,
        vol.Optional(
            ATTR_BACKGROUND_COLOR, default=DEFAULT_BACKGROUND_COLOR
        ): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up GeekMagic Live Display services."""

    async def async_show(call: ServiceCall) -> None:
        """Render and send the supplied text to a configured display."""
        clients: dict[str, GeekMagicClient] = hass.data.get(DOMAIN, {})
        entry_id = call.data.get(ATTR_ENTRY_ID)
        if entry_id is None and len(clients) == 1:
            client = next(iter(clients.values()))
        elif entry_id is not None and entry_id in clients:
            client = clients[entry_id]
        else:
            raise HomeAssistantError(
                "Specify entry_id when more than one GeekMagic display is configured"
            )

        try:
            image = await hass.async_add_executor_job(
                render_display,
                call.data[ATTR_TITLE],
                call.data[ATTR_MESSAGE],
                call.data[ATTR_FOREGROUND_COLOR],
                call.data[ATTR_BACKGROUND_COLOR],
            )
            await client.async_show(image)
        except GeekMagicError as err:
            raise HomeAssistantError(
                f"Unable to update GeekMagic display: {err}"
            ) from err

    hass.services.async_register(
        DOMAIN, SERVICE_SHOW, async_show, schema=SERVICE_SHOW_SCHEMA
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a GeekMagic display from a config entry."""
    client = GeekMagicClient(hass, entry.data["host"])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a GeekMagic display config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

"""Support for displaying live Home Assistant data on GeekMagic SmallTV."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_FRIENDLY_NAME, ATTR_UNIT_OF_MEASUREMENT, Platform
from homeassistant.core import Event, HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_state_change_event
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .api import GeekMagicClient, GeekMagicError, render_display
from .const import (
    ATTR_BACKGROUND_COLOR,
    ATTR_ENTRY_ID,
    ATTR_ENTITY_ID,
    ATTR_FOREGROUND_COLOR,
    ATTR_MESSAGE,
    ATTR_TITLE,
    DATA_CLIENTS,
    DATA_WATCHERS,
    DEFAULT_BACKGROUND_COLOR,
    DEFAULT_FOREGROUND_COLOR,
    DOMAIN,
    SERVICE_SHOW,
    SERVICE_SHOW_ENTITIES,
    SERVICE_STOP_WATCHING,
    SERVICE_WATCH_ENTITIES,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

DISPLAY_FIELDS = {
    vol.Optional(ATTR_ENTRY_ID): cv.string,
    vol.Optional(ATTR_TITLE, default="Home Assistant"): cv.string,
    vol.Optional(ATTR_FOREGROUND_COLOR, default=DEFAULT_FOREGROUND_COLOR): cv.string,
    vol.Optional(ATTR_BACKGROUND_COLOR, default=DEFAULT_BACKGROUND_COLOR): cv.string,
}

SERVICE_SHOW_SCHEMA = vol.Schema(
    {**DISPLAY_FIELDS, vol.Required(ATTR_MESSAGE): cv.string}
)
SERVICE_ENTITIES_SCHEMA = vol.Schema(
    {**DISPLAY_FIELDS, vol.Required(ATTR_ENTITY_ID): cv.entity_ids}
)
SERVICE_STOP_WATCHING_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTRY_ID): cv.string})


def _get_client(
    hass: HomeAssistant, entry_id: str | None
) -> tuple[str, GeekMagicClient]:
    """Return a configured client, resolving a single display automatically."""
    clients: dict[str, GeekMagicClient] = hass.data.get(DOMAIN, {}).get(
        DATA_CLIENTS, {}
    )
    if entry_id is None and len(clients) == 1:
        return next(iter(clients.items()))
    if entry_id is not None and entry_id in clients:
        return entry_id, clients[entry_id]
    raise HomeAssistantError(
        "Specify entry_id when more than one GeekMagic display is configured"
    )


def _format_entity_states(hass: HomeAssistant, entity_ids: list[str]) -> str:
    """Format current entity states for the constrained display."""
    lines = []
    for entity_id in entity_ids:
        state = hass.states.get(entity_id)
        if state is None:
            lines.append(f"{entity_id}: unavailable")
            continue
        name = state.attributes.get(ATTR_FRIENDLY_NAME, entity_id)
        unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT, "")
        lines.append(f"{name}: {state.state}{unit and f' {unit}'}")
    return "\n".join(lines)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up GeekMagic Live Display services."""

    async def async_show(call: ServiceCall) -> None:
        """Render and send the supplied text to a configured display."""
        entry_id, client = _get_client(hass, call.data.get(ATTR_ENTRY_ID))
        _stop_watching(hass, entry_id)
        await _async_show(
            hass,
            client,
            call.data[ATTR_TITLE],
            call.data[ATTR_MESSAGE],
            call.data[ATTR_FOREGROUND_COLOR],
            call.data[ATTR_BACKGROUND_COLOR],
        )

    async def async_show_entities(call: ServiceCall) -> None:
        """Display the current state of one or more Home Assistant entities."""
        entry_id, client = _get_client(hass, call.data.get(ATTR_ENTRY_ID))
        _stop_watching(hass, entry_id)
        await _async_show(
            hass,
            client,
            call.data[ATTR_TITLE],
            _format_entity_states(hass, call.data[ATTR_ENTITY_ID]),
            call.data[ATTR_FOREGROUND_COLOR],
            call.data[ATTR_BACKGROUND_COLOR],
        )

    async def async_watch_entities(call: ServiceCall) -> None:
        """Keep the display synchronized with one or more entity states."""
        entry_id, client = _get_client(hass, call.data.get(ATTR_ENTRY_ID))
        entity_ids = call.data[ATTR_ENTITY_ID]

        async def async_refresh() -> None:
            """Render the current states and report failed background updates."""
            try:
                await _async_show(
                    hass,
                    client,
                    call.data[ATTR_TITLE],
                    _format_entity_states(hass, entity_ids),
                    call.data[ATTR_FOREGROUND_COLOR],
                    call.data[ATTR_BACKGROUND_COLOR],
                )
            except HomeAssistantError as err:
                _LOGGER.error("Unable to update GeekMagic display: %s", err)

        _stop_watching(hass, entry_id)
        await _async_show(
            hass,
            client,
            call.data[ATTR_TITLE],
            _format_entity_states(hass, entity_ids),
            call.data[ATTR_FOREGROUND_COLOR],
            call.data[ATTR_BACKGROUND_COLOR],
        )

        @callback
        def async_state_changed(event: Event) -> None:
            """Refresh the display when a watched entity changes."""
            hass.async_create_task(async_refresh())

        hass.data[DOMAIN][DATA_WATCHERS][
            entry_id
        ] = async_track_state_change_event(hass, entity_ids, async_state_changed)

    async def async_stop_watching(call: ServiceCall) -> None:
        """Stop automatically updating a display."""
        entry_id, _ = _get_client(hass, call.data.get(ATTR_ENTRY_ID))
        _stop_watching(hass, entry_id)

    hass.services.async_register(
        DOMAIN, SERVICE_SHOW, async_show, schema=SERVICE_SHOW_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SHOW_ENTITIES,
        async_show_entities,
        schema=SERVICE_ENTITIES_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_WATCH_ENTITIES,
        async_watch_entities,
        schema=SERVICE_ENTITIES_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_WATCHING,
        async_stop_watching,
        schema=SERVICE_STOP_WATCHING_SCHEMA,
    )
    return True


async def _async_show(
    hass: HomeAssistant,
    client: GeekMagicClient,
    title: str,
    message: str,
    foreground_color: str,
    background_color: str,
) -> None:
    """Render and send text to a configured display."""
    try:
        image = await hass.async_add_executor_job(
            render_display, title, message, foreground_color, background_color
        )
        await client.async_show(image)
    except GeekMagicError as err:
        raise HomeAssistantError(f"Unable to update GeekMagic display: {err}") from err


def _stop_watching(hass: HomeAssistant, entry_id: str) -> None:
    """Stop the active entity watcher for a display, if one exists."""
    if unsubscribe := hass.data[DOMAIN][DATA_WATCHERS].pop(entry_id, None):
        unsubscribe()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a GeekMagic display from a config entry."""
    client = GeekMagicClient(hass, entry.data["host"])
    hass.data.setdefault(DOMAIN, {DATA_CLIENTS: {}, DATA_WATCHERS: {}})[
        DATA_CLIENTS
    ][entry.entry_id] = client
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a GeekMagic display config entry."""
    _stop_watching(hass, entry.entry_id)
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN][DATA_CLIENTS].pop(entry.entry_id)
    return unload_ok

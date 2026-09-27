"""Time entities for GeekMagic night mode."""
from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import GeekMagicClient
from .entity import GeekMagicEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the night-mode time selectors."""
    client: GeekMagicClient = hass.data["geekmagic_live_display"]["clients"][
        entry.entry_id
    ]
    async_add_entities(
        [
            GeekMagicNightStartTime(entry, client),
            GeekMagicNightEndTime(entry, client),
        ]
    )


class _GeekMagicNightTime(GeekMagicEntity, TimeEntity):
    """Base class for a night-mode time selector."""

    def __init__(
        self, entry: ConfigEntry, client: GeekMagicClient, suffix: str
    ) -> None:
        """Initialize the night-mode time selector."""
        super().__init__(entry, client, suffix)


class GeekMagicNightStartTime(_GeekMagicNightTime):
    """Select when night mode starts."""

    _attr_name = "Night mode start"
    _attr_icon = "mdi:clock-start"

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the night-mode start time."""
        super().__init__(entry, client, "night_start_time")

    async def async_update(self) -> None:
        """Update the night-mode start time."""
        self._attr_native_value = time(
            hour=(await self._client.async_get_night_mode())["t1"]
        )

    async def async_set_value(self, value: time) -> None:
        """Set the night-mode start time."""
        await self._client.async_set_night_mode(start_hour=value.hour)
        self._attr_native_value = time(hour=value.hour)
        self.async_write_ha_state()


class GeekMagicNightEndTime(_GeekMagicNightTime):
    """Select when night mode ends."""

    _attr_name = "Night mode end"
    _attr_icon = "mdi:clock-end"

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the night-mode end time."""
        super().__init__(entry, client, "night_end_time")

    async def async_update(self) -> None:
        """Update the night-mode end time."""
        self._attr_native_value = time(
            hour=(await self._client.async_get_night_mode())["t2"]
        )

    async def async_set_value(self, value: time) -> None:
        """Set the night-mode end time."""
        await self._client.async_set_night_mode(end_hour=value.hour)
        self._attr_native_value = time(hour=value.hour)
        self.async_write_ha_state()

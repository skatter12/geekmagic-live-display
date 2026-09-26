"""Shared entity support for GeekMagic Live Display."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .api import GeekMagicClient
from .const import DOMAIN


class GeekMagicEntity(Entity):
    """Base entity for a GeekMagic SmallTV."""

    _attr_has_entity_name = True

    def __init__(
        self, entry: ConfigEntry, client: GeekMagicClient, suffix: str
    ) -> None:
        """Initialize the entity."""
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_{suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="GeekMagic",
            model="SmallTV-Ultra",
        )

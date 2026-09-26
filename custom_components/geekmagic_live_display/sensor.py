"""Sensor entities for GeekMagic display diagnostics."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import GeekMagicClient
from .const import ATTR_TOTAL_SPACE
from .entity import GeekMagicEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the display storage sensor."""
    client: GeekMagicClient = hass.data["geekmagic_live_display"]["clients"][
        entry.entry_id
    ]
    async_add_entities([GeekMagicFreeSpaceSensor(entry, client)])


class GeekMagicFreeSpaceSensor(GeekMagicEntity, SensorEntity):
    """Represent free image storage on the SmallTV."""

    _attr_name = "Free space"
    _attr_device_class = SensorDeviceClass.DATA_SIZE
    _attr_native_unit_of_measurement = UnitOfInformation.BYTES

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the free-space sensor."""
        super().__init__(entry, client, "free_space")

    async def async_update(self) -> None:
        """Update the available image storage."""
        storage = await self._client.async_get_storage()
        self._attr_native_value = storage["free"]
        self._attr_extra_state_attributes = {ATTR_TOTAL_SPACE: storage["total"]}

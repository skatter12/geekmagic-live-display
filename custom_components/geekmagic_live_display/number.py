"""Number entities for GeekMagic display brightness settings."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import GeekMagicClient
from .entity import GeekMagicEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the display brightness controls."""
    client: GeekMagicClient = hass.data["geekmagic_live_display"]["clients"][
        entry.entry_id
    ]
    async_add_entities(
        [
            GeekMagicBrightnessNumber(entry, client),
            GeekMagicNightBrightnessNumber(entry, client),
            GeekMagicImageIntervalNumber(entry, client),
        ]
    )


class GeekMagicBrightnessNumber(GeekMagicEntity, NumberEntity):
    """Represent the SmallTV brightness."""

    _attr_name = "Brightness"
    _attr_native_min_value = -10
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the brightness number."""
        super().__init__(entry, client, "brightness")

    async def async_update(self) -> None:
        """Update the brightness."""
        self._attr_native_value = await self._client.async_get_brightness()

    async def async_set_native_value(self, value: float) -> None:
        """Set the brightness."""
        self._attr_native_value = int(value)
        await self._client.async_set_brightness(int(value))
        self.async_write_ha_state()


class GeekMagicNightBrightnessNumber(GeekMagicEntity, NumberEntity):
    """Represent the brightness used in night mode."""

    _attr_name = "Night mode brightness"
    _attr_native_min_value = -10
    _attr_native_max_value = 100
    _attr_native_step = 1

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the night-mode brightness."""
        super().__init__(entry, client, "night_brightness")

    async def async_update(self) -> None:
        """Update the night-mode brightness."""
        self._attr_native_value = (await self._client.async_get_night_mode())["b2"]

    async def async_set_native_value(self, value: float) -> None:
        """Set the night-mode brightness."""
        self._attr_native_value = int(value)
        await self._client.async_set_night_mode(brightness=int(value))
        self.async_write_ha_state()


class GeekMagicImageIntervalNumber(GeekMagicEntity, NumberEntity):
    """Represent the photo-album image interval."""

    _attr_name = "Image interval"
    _attr_native_min_value = 1
    _attr_native_max_value = 3600
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "s"

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the image interval."""
        super().__init__(entry, client, "image_interval")

    async def async_update(self) -> None:
        """Update the image interval."""
        self._attr_native_value = (await self._client.async_get_album())["i_i"]

    async def async_set_native_value(self, value: float) -> None:
        """Set the image interval."""
        self._attr_native_value = int(value)
        await self._client.async_set_album(interval=int(value))
        self.async_write_ha_state()

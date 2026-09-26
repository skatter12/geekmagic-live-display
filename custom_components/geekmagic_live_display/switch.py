"""Switch entity for GeekMagic night mode."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import GeekMagicClient
from .entity import GeekMagicEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the night-mode switch."""
    client: GeekMagicClient = hass.data["geekmagic_live_display"]["clients"][
        entry.entry_id
    ]
    async_add_entities([GeekMagicNightModeSwitch(entry, client)])


class GeekMagicNightModeSwitch(GeekMagicEntity, SwitchEntity):
    """Represent the SmallTV night mode."""

    _attr_name = "Night mode"

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the night-mode switch."""
        super().__init__(entry, client, "night_mode")

    async def async_update(self) -> None:
        """Update the night-mode state."""
        self._attr_is_on = bool((await self._client.async_get_night_mode())["en"])

    async def async_turn_on(self, **kwargs: object) -> None:
        """Enable night mode."""
        await self._client.async_set_night_mode(enabled=1)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: object) -> None:
        """Disable night mode."""
        await self._client.async_set_night_mode(enabled=0)
        self._attr_is_on = False
        self.async_write_ha_state()

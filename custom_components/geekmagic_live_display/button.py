"""Button entity for GeekMagic display maintenance."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import GeekMagicClient
from .entity import GeekMagicEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the display reboot button."""
    client: GeekMagicClient = hass.data["geekmagic_live_display"]["clients"][
        entry.entry_id
    ]
    async_add_entities([GeekMagicRebootButton(entry, client)])


class GeekMagicRebootButton(GeekMagicEntity, ButtonEntity):
    """Provide an explicit reboot action for the SmallTV."""

    _attr_name = "Reboot"

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the reboot button."""
        super().__init__(entry, client, "reboot")

    async def async_press(self) -> None:
        """Reboot the display."""
        await self._client.async_reboot()

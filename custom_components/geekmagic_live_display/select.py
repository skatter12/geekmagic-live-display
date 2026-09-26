"""Select entity for GeekMagic display themes."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import GeekMagicClient
from .const import THEMES
from .entity import GeekMagicEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the display theme selector."""
    client: GeekMagicClient = hass.data["geekmagic_live_display"]["clients"][
        entry.entry_id
    ]
    async_add_entities([GeekMagicThemeSelect(entry, client)])


class GeekMagicThemeSelect(GeekMagicEntity, SelectEntity):
    """Represent the currently selected SmallTV theme."""

    _attr_name = "Theme"
    _attr_options = list(THEMES.values())

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the theme selector."""
        super().__init__(entry, client, "theme")
        self._attr_current_option = THEMES["3"]

    async def async_update(self) -> None:
        """Update the selected theme."""
        self._attr_current_option = THEMES.get(
            await self._client.async_get_theme(), THEMES["3"]
        )

    async def async_select_option(self, option: str) -> None:
        """Select a display theme."""
        theme = next(key for key, value in THEMES.items() if value == option)
        await self._client.async_set_theme(theme)
        self._attr_current_option = option
        self.async_write_ha_state()

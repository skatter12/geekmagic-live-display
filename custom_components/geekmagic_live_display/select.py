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
    async_add_entities(
        [
            GeekMagicThemeSelect(entry, client),
            GeekMagicImageSelect(entry, client),
            GeekMagicSmallImageSelect(entry, client),
        ],
        update_before_add=True,
    )


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


class _GeekMagicFileSelect(GeekMagicEntity, SelectEntity):
    """Base class for a selectable SmallTV file."""

    _attr_options = []

    def __init__(
        self,
        entry: ConfigEntry,
        client: GeekMagicClient,
        suffix: str,
        directory: str,
    ) -> None:
        """Initialize the file selector."""
        super().__init__(entry, client, suffix)
        self._directory = directory
        self._files: dict[str, str] = {}

    async def async_update(self) -> None:
        """Load available files from the display."""
        files = await self._client.async_get_files(self._directory)
        self._files = {file_path.rsplit("/", 1)[-1]: file_path for file_path in files}
        self._attr_options = list(self._files)
        if self._attr_current_option not in self._files:
            self._attr_current_option = None


class GeekMagicImageSelect(_GeekMagicFileSelect):
    """Select a full-screen image from the SmallTV image folder."""

    _attr_name = "Image"

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the image selector."""
        super().__init__(entry, client, "image", "/image/")

    async def async_select_option(self, option: str) -> None:
        """Select the full-screen image."""
        await self._client.async_set_image(self._files[option])
        self._attr_current_option = option
        self.async_write_ha_state()


class GeekMagicSmallImageSelect(_GeekMagicFileSelect):
    """Select a small weather-theme image from the SmallTV GIF folder."""

    _attr_name = "Small image"

    def __init__(self, entry: ConfigEntry, client: GeekMagicClient) -> None:
        """Initialize the small-image selector."""
        super().__init__(entry, client, "small_image", "/gif/")

    async def async_select_option(self, option: str) -> None:
        """Select the small weather-theme image."""
        await self._client.async_set_small_image(self._files[option])
        self._attr_current_option = option
        self.async_write_ha_state()

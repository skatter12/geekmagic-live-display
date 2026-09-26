"""HTTP client and image renderer for GeekMagic SmallTV-Ultra."""
from __future__ import annotations

import asyncio
import io
import textwrap

import aiohttp
from PIL import Image, ImageColor, ImageDraw, ImageFont

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DISPLAY_SIZE, LIVE_IMAGE_NAME, PHOTO_THEME


class GeekMagicError(Exception):
    """Raised when the display cannot be updated."""


class GeekMagicClient:
    """Communicate with a GeekMagic SmallTV-Ultra."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize the client."""
        self._session = async_get_clientsession(hass)
        self._base_url = f"http://{host}"

    async def async_validate(self) -> dict[str, str]:
        """Return model information from the display."""
        return await self._async_get_json("/v.json")

    async def async_show(self, image: bytes) -> None:
        """Upload an image and make it the active photo-album image."""
        await self._async_get("/set", params={"theme": PHOTO_THEME})

        data = aiohttp.FormData()
        data.add_field(
            "image",
            image,
            filename=LIVE_IMAGE_NAME,
            content_type="image/jpeg",
        )
        await self._async_post("/doUpload", params={"dir": "/image/"}, data=data)
        await self._async_get("/set", params={"img": LIVE_IMAGE_NAME})

    async def _async_get_json(self, path: str) -> dict[str, str]:
        """Request JSON from the display."""
        try:
            async with asyncio.timeout(10):
                async with self._session.get(f"{self._base_url}{path}") as response:
                    response.raise_for_status()
                    data = await response.json(content_type=None)
        except (asyncio.TimeoutError, aiohttp.ClientError, ValueError) as err:
            raise GeekMagicError(str(err)) from err

        if not isinstance(data, dict):
            raise GeekMagicError(f"Unexpected response from {path}")
        return data

    async def _async_get(self, path: str, *, params: dict[str, str]) -> None:
        """Send a GET command to the display."""
        try:
            async with asyncio.timeout(10):
                async with self._session.get(
                    f"{self._base_url}{path}", params=params
                ) as response:
                    response.raise_for_status()
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            raise GeekMagicError(str(err)) from err

    async def _async_post(
        self, path: str, *, params: dict[str, str], data: aiohttp.FormData
    ) -> None:
        """Upload content to the display."""
        try:
            async with asyncio.timeout(30):
                async with self._session.post(
                    f"{self._base_url}{path}", params=params, data=data
                ) as response:
                    response.raise_for_status()
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            raise GeekMagicError(str(err)) from err


def render_display(
    title: str, message: str, foreground_color: str, background_color: str
) -> bytes:
    """Render a title and message as the 240x240 JPEG required by the display."""
    try:
        foreground = ImageColor.getrgb(foreground_color)
        background = ImageColor.getrgb(background_color)
    except ValueError as err:
        raise GeekMagicError(f"Invalid color: {err}") from err

    image = Image.new("RGB", (DISPLAY_SIZE, DISPLAY_SIZE), background)
    draw = ImageDraw.Draw(image)
    title_font = _get_font(22)
    message_font = _get_font(16)

    _draw_centered(draw, title, 14, title_font, foreground)
    draw.line((16, 48, DISPLAY_SIZE - 16, 48), fill=foreground, width=1)

    y_position = 64
    for line in _wrap_text(draw, message, message_font, DISPLAY_SIZE - 32):
        _draw_centered(draw, line, y_position, message_font, foreground)
        y_position += 24
        if y_position > DISPLAY_SIZE - 28:
            break

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=90, optimize=True)
    return output.getvalue()


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Use a scalable font when Pillow can locate it."""
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _wrap_text(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int
) -> list[str]:
    """Wrap text to fit the display width while preserving explicit line breaks."""
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = textwrap.wrap(paragraph, width=28, break_long_words=True) or [""]
        for line in words:
            while draw.textbbox((0, 0), line, font=font)[2] > width and len(line) > 1:
                line = line[:-1]
            lines.append(line)
    return lines


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    y_position: int,
    font: ImageFont.ImageFont,
    color: tuple[int, int, int],
) -> None:
    """Draw text centered horizontally."""
    bounding_box = draw.textbbox((0, 0), text, font=font)
    x_position = (DISPLAY_SIZE - (bounding_box[2] - bounding_box[0])) // 2
    draw.text((x_position, y_position), text, font=font, fill=color)

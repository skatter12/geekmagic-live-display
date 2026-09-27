"""HTTP client and image renderer for GeekMagic SmallTV-Ultra."""
from __future__ import annotations

import asyncio
import io
import os
import re
import urllib.error
import urllib.parse
import urllib.request

import aiohttp
from PIL import Image, ImageColor, ImageDraw, ImageFont

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DISPLAY_SIZE, LIVE_IMAGE_NAME, PHOTO_THEME

_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")


class GeekMagicError(Exception):
    """Raised when the display cannot be updated."""


def _fetch_text(url: str) -> str:
    """Request text from the display, tolerating its malformed headers.

    Blocking urllib is used because the display's /filelist endpoint sends a
    duplicated Content-Length header, which aiohttp rejects.
    """
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8", errors="replace")


def _post_image(url: str, filename: str, image: bytes, params: dict[str, str]) -> None:
    """Upload an image to the display, tolerating its malformed headers.

    Blocking urllib is used because the display's /doUpload endpoint sends a
    duplicated Content-Length header, which aiohttp rejects.
    """
    boundary = "----geekmagicboundary"
    body = io.BytesIO()
    body.write(f"--{boundary}\r\n".encode())
    body.write(
        f"Content-Disposition: form-data; name=\"image\"; "
        f"filename=\"{filename}\"\r\n".encode()
    )
    body.write(b"Content-Type: image/jpeg\r\n\r\n")
    body.write(image)
    body.write(f"\r\n--{boundary}--\r\n".encode())
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{url}?{query}", data=body.getvalue(), method="POST"
    )
    request.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()


class GeekMagicClient:
    """Communicate with a GeekMagic SmallTV-Ultra."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize the client."""
        self._hass = hass
        self._session = async_get_clientsession(hass)
        self._base_url = f"http://{host}"

    async def async_validate(self) -> dict[str, str]:
        """Return model information from the display."""
        return await self._async_get_json("/v.json")

    async def async_show(self, image: bytes) -> None:
        """Upload an image and make it the active photo-album image."""
        await self._async_get("/set", params={"theme": PHOTO_THEME})

        # The display sends a duplicated Content-Length header on /doUpload,
        # which aiohttp rejects. urllib tolerates it, so upload in a worker.
        await self._hass.async_add_executor_job(
            _post_image,
            f"{self._base_url}/doUpload",
            LIVE_IMAGE_NAME,
            image,
            {"dir": "/image/"},
        )
        await self._async_get("/set", params={"img": f"/image/{LIVE_IMAGE_NAME}"})

    async def async_get_theme(self) -> str:
        """Return the currently selected theme."""
        return str((await self._async_get_json("/app.json")).get("theme", "3"))

    async def async_set_theme(self, theme: str) -> None:
        """Select a built-in display theme."""
        await self._async_set(theme=theme)

    async def async_get_brightness(self) -> int:
        """Return the current display brightness."""
        return int((await self._async_get_json("/brt.json"))["brt"])

    async def async_set_brightness(self, brightness: int) -> None:
        """Set the display brightness."""
        await self._async_set(brt=brightness)

    async def async_get_night_mode(self) -> dict[str, int]:
        """Return the night-mode settings."""
        data = await self._async_get_json("/timebrt.json")
        return {key: int(data[key]) for key in ("en", "t1", "t2", "b2")}

    async def async_set_night_mode(
        self,
        *,
        enabled: int | None = None,
        start_hour: int | None = None,
        end_hour: int | None = None,
        brightness: int | None = None,
    ) -> None:
        """Update one or more night-mode settings."""
        settings = await self.async_get_night_mode()
        await self._async_set(
            en=settings["en"] if enabled is None else enabled,
            t1=settings["t1"] if start_hour is None else start_hour,
            t2=settings["t2"] if end_hour is None else end_hour,
            b1=50,
            b2=settings["b2"] if brightness is None else brightness,
        )

    async def async_reboot(self) -> None:
        """Reboot the display."""
        await self._async_set(reboot=1)

    async def async_get_storage(self) -> dict[str, int]:
        """Return total and free storage space in bytes."""
        data = await self._async_get_json("/space.json")
        return {key: int(data[key]) for key in ("total", "free")}

    async def async_get_album(self) -> dict[str, int]:
        """Return the image slideshow settings."""
        data = await self._async_get_json("/album.json")
        return {key: int(data[key]) for key in ("autoplay", "i_i")}

    async def async_set_album(
        self, *, autoplay: int | None = None, interval: int | None = None
    ) -> None:
        """Update one or more image slideshow settings."""
        settings = await self.async_get_album()
        await self._async_set(
            autoplay=settings["autoplay"] if autoplay is None else autoplay,
            i_i=settings["i_i"] if interval is None else interval,
        )

    async def async_get_files(self, directory: str) -> list[str]:
        """Return the files available in a display directory."""
        response = await self._async_get_text("/filelist", params={"dir": directory})
        return [
            file_path.replace("//", "/")
            for file_path in re.findall(r"<a href='([^']+)'>", response)
        ]

    async def async_set_image(self, file_path: str) -> None:
        """Select a full-screen photo-album image."""
        await self._async_set(img=file_path)

    async def async_set_small_image(self, file_path: str) -> None:
        """Select the small image shown by the weather themes."""
        await self._async_set(gif=file_path)

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

    async def _async_set(self, **params: str | int) -> None:
        """Send settings to the display."""
        await self._async_get("/set", params=params)

    async def _async_get(
        self, path: str, *, params: dict[str, str | int]
    ) -> None:
        """Send a GET command to the display."""
        try:
            async with asyncio.timeout(10):
                async with self._session.get(
                    f"{self._base_url}{path}", params=params
                ) as response:
                    response.raise_for_status()
        except (asyncio.TimeoutError, aiohttp.ClientError):
            # The display can send a duplicated Content-Length header, which
            # aiohttp rejects. Retry with urllib, which tolerates it.
            url = f"{self._base_url}{path}?{urllib.parse.urlencode(params)}"
            try:
                await self._hass.async_add_executor_job(_fetch_text, url)
            except (TimeoutError, urllib.error.URLError) as err:
                raise GeekMagicError(str(err)) from err

    async def _async_get_text(
        self, path: str, *, params: dict[str, str | int]
    ) -> str:
        """Request text from the display."""
        try:
            async with asyncio.timeout(10):
                async with self._session.get(
                    f"{self._base_url}{path}", params=params
                ) as response:
                    response.raise_for_status()
                    return await response.text()
        except (asyncio.TimeoutError, aiohttp.ClientError):
            # The display sends a duplicated Content-Length header on /filelist,
            # which aiohttp rejects. Retry with urllib, which tolerates it.
            url = f"{self._base_url}{path}?{urllib.parse.urlencode(params)}"
            try:
                return await self._hass.async_add_executor_job(_fetch_text, url)
            except (TimeoutError, urllib.error.URLError) as err:
                raise GeekMagicError(str(err)) from err


def render_display(
    title: str, message: str, foreground_color: str, background_color: str
) -> bytes:
    """Render the display as stacked bands of equally sized text.

    The title takes the top band and every non-empty line of the message takes
    one band of its own, so passing two entities fills the 240x240 screen with
    three equally large lines. All lines share a single font size: the largest
    one that still lets the longest line fit, so the screen looks uniform.
    """
    try:
        foreground = ImageColor.getrgb(foreground_color)
        background = ImageColor.getrgb(background_color)
    except ValueError as err:
        raise GeekMagicError(f"Invalid color: {err}") from err

    lines = [title]
    lines += [line.strip() for line in message.splitlines() if line.strip()]

    image = Image.new("RGB", (DISPLAY_SIZE, DISPLAY_SIZE), background)
    draw = ImageDraw.Draw(image)
    count = len(lines)
    bands = [
        (index * DISPLAY_SIZE // count, (index + 1) * DISPLAY_SIZE // count)
        for index in range(count)
    ]
    band_height = min(bottom - top for top, bottom in bands)

    font = _fit_font(draw, lines, DISPLAY_SIZE - 8, band_height - 8, band_height)
    for text, (top, bottom) in zip(lines, bands):
        _draw_centered(draw, text, top, bottom - top, font, foreground)

    output = io.BytesIO()
    image.save(output, format="JPEG", quality=90, optimize=True)
    return output.getvalue()


def _fit_font(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    max_width: int,
    max_height: int,
    max_size: int,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Return the largest font size where every line fits in the given space."""
    for size in range(max_size, 5, -1):
        font = _get_font(size)
        if all(
            _fits(draw, text, font, max_width, max_height) for text in lines
        ):
            return font
    return _get_font(6)


def _fits(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    max_height: int,
) -> bool:
    """Return whether the text fits within the given space."""
    left, upper, right, lower = draw.textbbox((0, 0), text, font=font)
    return (
        right - left <= max_width and lower - upper <= max_height
    )


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load the bundled DejaVu Sans Bold font at the requested size."""
    for candidate in (
        os.path.join(_FONT_DIR, "DejaVuSans-Bold.ttf"),
        os.path.join(_FONT_DIR, "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue

    # Last resort: Pillow's built-in font, which only honours a size on
    # Pillow 10.1 and newer.
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    top: int,
    band_height: int,
    font: ImageFont.ImageFont,
    color: tuple[int, int, int],
) -> None:
    """Draw text centered both horizontally and vertically inside one band."""
    left, upper, right, lower = draw.textbbox((0, 0), text, font=font)
    x_position = (DISPLAY_SIZE - (right - left)) // 2 - left
    y_position = top + (band_height - (lower - upper)) // 2 - upper
    draw.text((x_position, y_position), text, font=font, fill=color)

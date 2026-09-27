# GeekMagic Live Display

Turn a GeekMagic SmallTV-Ultra into a compact Home Assistant status display.
This integration controls the display over its local HTTP API and can show live
states from any Home Assistant entity as a 240×240 image.

## Changelog

### 1.3.10

- All lines now share a single font size instead of being sized individually,
  so the screen looks uniform. The shared size is the largest one that still
  lets the longest line fit, which means the title sets the size for the
  entity values below it.

### 1.3.9

- **Fix unreadably small text.** The container has no system fonts, so Pillow
  silently fell back to its built-in bitmap font, which ignores the requested
  size. DejaVu Sans Bold and Regular are now bundled in `fonts/` and loaded
  from there, so the rendered text finally honours the requested size.
- The screen is now split into as many equally sized bands as there are lines:
  the title in the top band and every entity value in a band of its own. Two
  entities therefore produce three equally large lines, each scaled up until
  the text fills its band.
- Entity values are uppercased for legibility at the large font size.

### 1.3.8

- Redesign the live-data screen as three equal bands, one line of text each:
  the title on top, the entity value in the middle and the current time at
  the bottom. Each line is centered in its band and the font is sized
  automatically so the text fills a third of the 240×240 display.
- `watch_entities` / `show_entities` no longer prefix the value with the
  entity name, so the middle band shows just the value (for example `33`).

### 1.3.7

- Fix the live-data text staying tiny. The bundled font was not found, so
  Pillow fell back to a small bitmap font that ignores the requested size.
  Load DejaVuSans from its system path and increase the sizes to 40px title
  and 30px message.

### 1.3.6

- Make the live-data text larger and easier to read on the 240×240 display.
  Title is now 34px and message text 26px (previously 22px and 16px).

### 1.3.5

- Fix the live-data image not being selected after upload. The display
  expects the full path (`/image/home_assistant_live.jpg`), but only the
  filename was sent, so the previous image stayed on screen.

### 1.3.4

- Fix the live-data services (`show`, `show_entities`, `watch_entities`)
  failing with "Duplicate Content-Length". The display sends the same
  duplicated header on `/doUpload` as it does on `/filelist`, so the image
  upload now also falls back to `urllib`.

### 1.3.3

- Add **Night mode start** and **Night mode end** time selectors so the
  night-mode period can be chosen as a time range (for example 20:00-05:00)
  instead of entering hours as numbers. The previous "Night mode start hour"
  and "Night mode end hour" number entities have been replaced by these.

### 1.3.2

- Fix the **Image** and **Small image** selectors staying empty and
  unavailable. The display's `/filelist` endpoint sends a duplicated
  `Content-Length` header, which aiohttp rejects. The file list is now fetched
  with aiohttp first and falls back to `urllib` when aiohttp rejects the
  response.

### 1.3.1

- Current release.

## Features

- Select all seven built-in SmallTV themes: weather clocks, forecast, photo
  album, clock styles, and simple weather clock.
- Control brightness, night mode, night-mode schedule, and night brightness.
- Control photo-album autoplay and image interval.
- Select full-screen images from the `/image/` folder and small weather-theme
  images from the `/gif/` folder.
- Monitor remaining SmallTV storage with a diagnostic free-space sensor.
- Reboot the display from Home Assistant.
- Render custom text with `geekmagic_live_display.show`.
- Display one or more entity states with
  `geekmagic_live_display.show_entities`.
- Keep the display automatically synchronized with selected entities through
  `geekmagic_live_display.watch_entities`.

## Installation

### HACS

1. In HACS, open **Integrations** and select the three-dot menu.
2. Select **Custom repositories**.
3. Add `https://github.com/skatter12/geekmagic-live-display` with category
   **Integration**.
4. Install **GeekMagic Live Display**, restart Home Assistant, and add it from
   **Settings → Devices & services**.

### Manual

Copy this directory to
`config/custom_components/geekmagic_live_display`, restart Home Assistant, then
add **GeekMagic Live Display** from **Settings → Devices & services**. Enter the
display's local IP address.

## Examples

The services select the only configured display automatically. Add `entry_id`
when more than one display is configured.

### Custom text

```yaml
service: geekmagic_live_display.show
data:
  title: Vaskemaskine
  message: >
    Status: {{ states('sensor.washing_machine_status') }}
    Tid tilbage: {{ states('sensor.washing_machine_remaining_time') }}
  foreground_color: "#ffffff"
  background_color: "#16324f"
```

### Automatically updated entity view

```yaml
service: geekmagic_live_display.watch_entities
data:
  title: Vaskemaskine
  entity_id:
    - sensor.washing_machine_status
    - sensor.washing_machine_remaining_time
```

Call `geekmagic_live_display.stop_watching` to stop automatic updates. Starting
a new `show`, `show_entities`, or `watch_entities` service call replaces the
previous watcher for that display.

## Night mode

Night mode does not switch the display off. When it is enabled, the SmallTV
automatically lowers its brightness to **Night mode brightness** between
**Night mode start hour** and **Night mode end hour**. The Night mode entity
also exposes the currently configured start hour, end hour, and brightness as
attributes.

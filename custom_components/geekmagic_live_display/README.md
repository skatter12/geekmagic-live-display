# GeekMagic Live Display

Turn a GeekMagic SmallTV-Ultra into a compact Home Assistant status display.
This integration controls the display over its local HTTP API and can show live
states from any Home Assistant entity as a 240×240 image.

## Features

- Select all seven built-in SmallTV themes: weather clocks, forecast, photo
  album, clock styles, and simple weather clock.
- Control brightness, night mode, night-mode schedule, and night brightness.
- Control photo-album autoplay and image interval.
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

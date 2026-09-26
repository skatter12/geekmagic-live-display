# GeekMagic Live Display

This custom integration sends live Home Assistant data to a GeekMagic
SmallTV-Ultra. It renders a 240×240 JPEG, uploads it to the device, and selects
the photo-album theme.

## Installation

Copy this `geekmagic_live_display` directory to
`config/custom_components/geekmagic_live_display`, restart Home Assistant, then
add **GeekMagic Live Display** from **Settings → Devices & services**. Enter the
display's local IP address.

## Automation example

The service automatically selects the display when only one is configured. Add
`entry_id` only when multiple displays are configured. The service data supports
normal Home Assistant templates:

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

Trigger the automation on the relevant washing-machine entities. Each trigger
uploads a new `home_assistant_live.jpg` to the SmallTV.

## Built-in controls

The integration adds a theme selector for all seven SmallTV views, a brightness
control, night-mode toggle, night-mode start and end hour controls, night-mode
brightness, and a reboot button.

## Easy live views for other devices

Use `geekmagic_live_display.show_entities` to render the friendly name, current
state, and unit of one or more entities once. Use
`geekmagic_live_display.watch_entities` to do the same and automatically refresh
the display whenever any selected entity changes:

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

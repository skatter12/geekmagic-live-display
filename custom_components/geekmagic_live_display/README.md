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

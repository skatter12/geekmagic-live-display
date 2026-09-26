# GeekMagic Live Display

A Home Assistant custom integration that shows live entity data on a GeekMagic
SmallTV-Ultra. The integration renders text to the display's native 240×240
JPEG format and sends it over the device's local HTTP API.

## HACS installation

1. In HACS, open **Integrations** and select the three-dot menu.
2. Choose **Custom repositories**.
3. Add `https://github.com/skatter12/geekmagic-live-display` as category
   **Integration**.
4. Find and install **GeekMagic Live Display**, then restart Home Assistant.
5. Add **GeekMagic Live Display** in **Settings ? Devices & services** and
   provide the SmallTV's local IP address.

## Using live data

Call `geekmagic_live_display.show` from an automation whenever the state of an
entity changes. With one configured SmallTV, it is selected automatically:

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

When multiple displays are configured, add that integration's `entry_id` to
the service data.

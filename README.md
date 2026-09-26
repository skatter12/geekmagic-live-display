# GeekMagic Live Display

A Home Assistant custom integration for GeekMagic SmallTV-Ultra. It provides
native controls for the display and renders live Home Assistant data as a
240×240 JPEG sent through the display's local HTTP API.

## HACS installation

1. In HACS, open **Integrations** and select the three-dot menu.
2. Choose **Custom repositories**.
3. Add `https://github.com/skatter12/geekmagic-live-display` as category
   **Integration**.
4. Install **GeekMagic Live Display**, then restart Home Assistant.
5. Add **GeekMagic Live Display** in **Settings ? Devices & services** and
   provide the SmallTV's local IP address.

## Controls

The integration adds a selector for every built-in SmallTV theme, brightness,
night-mode enablement, night-mode start and end hour, night-mode brightness,
and a reboot button.

## Showing Home Assistant data

Use `geekmagic_live_display.show_entities` to display selected entities once.
Use `geekmagic_live_display.watch_entities` to automatically refresh the
screen whenever a selected entity changes:

```yaml
service: geekmagic_live_display.watch_entities
data:
  title: Vaskemaskine
  entity_id:
    - sensor.washing_machine_status
    - sensor.washing_machine_remaining_time
```

See the integration's service descriptions in Home Assistant for all fields.

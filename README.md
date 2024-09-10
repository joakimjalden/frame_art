# A Home Assistant Integration for Samsung The Frame Art Mode

### Background

This bare-bones custom Home Assistant (HA) component controls art mode on (newer) Samsung The Frame TVs. It is intended to be a proof of concept implementation until I can either contribute to the HA development or get traction for a similar feature request. It uses the `samsung-tv-ws-api` Python API, also used by the official `samsungtv` platform in HA. The Python API supports many more features than turning the art mode on and off, but since I could not get these to work, only the most basic switch feature was implemented.

### Installation

The integration can be installed by copying the files to `/config/custom_components/frame_art`  and adding something similar to your `configurations.yaml`,

```
switch:
  - platform: frame_art
    switches:
      my_tv_art_mode:
        resource: 192.168.xxx.xxx
```

### How it works or is intended to work

When the TV is on, the switch can be used to turn art mode for the TV on and off. When the TV is powered off or in standby mode (black screen), it does not respond to requests through the art mode API, so the switch is stuck at off, although maybe an unavailable state would have been more logical. Any reasonable use of automation will also have to test whether the TV is on, which can be done through the standard Samsung TV integration. I have tested the integration on my 55in The Frame (2022) with Firmware 1640. Feedback on if it works with other models is appreciated.

## Why not implement directly in the Samsung TV integration?

This would naturally be the way to go long term, especially given that both integrations rely on  `samsung-tv-ws-api` (at least for newer TVs), but my programming skills are not yet good enough to contribute with a PR. This may happen before a feature request is heard; maybe not.

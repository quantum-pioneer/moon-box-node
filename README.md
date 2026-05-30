# Moon Box Node

Moon Box Node is an ESPHome based Moon calculation project for Home Assistant and a real time DIY Moon Box display.

The goal is to calculate useful Moon data locally on an ESP32 and send that data into Home Assistant. This data can then be used for a physical Moon display, dashboard cards, automations, and future display hardware.

## Project Goal

I am building a physical Moon Box that can show the Moon in a more accurate and useful way than a simple phase icon.

The project is meant to calculate and display real Moon data such as phase, illumination, altitude, azimuth, horizon status, and upcoming lunar events. Eventually, this data will be used with one or more displays to show the Moon moving across the sky and changing phase over time.

## Main Features

* Moon phase name
* Moon illumination percentage
* Moon altitude
* Moon azimuth
* Sun altitude
* Moon and Sun angular separation
* Moon distance in kilometers and miles
* Last new moon
* Next new moon
* Next first quarter
* Next full moon
* Next last quarter
* Current lunation length
* Moon above horizon status
* Moon visible in clear sky status
* Eclipse possible at next full moon estimate
* WiFi signal and diagnostic entities
* Home Assistant integration through ESPHome

* ## Before Flashing

This YAML is a public template.

Before flashing it to your own ESP32, you must add your own network configuration and location values.

The public version does not include WiFi credentials, private location coordinates, or personal light/output functions.

You need to add your own:

- WiFi or Ethernet configuration
- Latitude
- Longitude
- Elevation in meters
- API encryption key if desired
- OTA settings if desired
- Any light, LED, display, or button functions for your own hardware

The included Moon calculations are the core of the project. Hardware-specific features should be customized for each build.

## Hardware

This project is currently built around an ESP32 running ESPHome.

The ESP32 calculates Moon data and publishes it to Home Assistant. The data can then be used by Home Assistant dashboards, automations, and future Moon Box display hardware.

Planned or possible hardware includes:

* ESP32 board
* ESPHome
* Home Assistant
* Round display for the Moon phase view
* Rectangular display for Moon position and sky data
* Enclosure for the physical Moon Box
* Optional buttons, LEDs, or other status indicators

## Home Assistant

The ESP32 exposes Moon data as Home Assistant entities through ESPHome.

These entities can be used for:

* Dashboards
* Automations
* Physical display logic
* Moon phase lighting effects
* Visibility status
* Future local AI or home monitoring projects

## Accuracy Goals

This project is intended to be more accurate than a basic Moon phase sensor.

The current goal is to calculate:

* Local Moon altitude
* Local Moon azimuth
* Moon illumination percentage
* Moon phase events
* Horizon visibility
* Clear sky visibility logic
* Apparent Moon altitude using local observer data

This project is still experimental, and the calculations may continue to improve over time.

## Important Security Note

Do not upload your real ESPHome `secrets.yaml` file to GitHub.

This project uses ESPHome secret references such as:

```yaml
!secret wifi_ssid
!secret wifi_password
!secret moon_node_api_key
!secret moon_node_ota_password
```

The real values should stay only in Home Assistant or in your local ESPHome secrets file.

## Project Status

This is an early working project.

The current focus is:

1. Accurate Moon calculations
2. Reliable ESPHome entities
3. Home Assistant integration
4. Preparing the project for a physical Moon Box display
5. Making the project clear enough for others to understand, use, and improve

## Future Plans

Possible future improvements include:

* Physical round Moon phase display
* Rectangular Moon sky position display
* Better visual Moon rendering
* More accurate visibility logic using weather data
* Moonrise and moonset display
* GitHub community improvements
* Documentation for setup and flashing
* Example Home Assistant dashboard cards

## License

MIT

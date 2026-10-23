# Moon Box Node

An ESPHome project that calculates Moon data locally on an ESP32 and publishes it to Home Assistant. The goal is a physical Moon Box with a round phase display and a second view showing the Moon's position and upcoming events.

**Work in progress:** calculation/entity code is available; physical displays and complete astronomical accuracy validation remain unfinished. No display driver, weather feed or finished enclosure is included.

## Current features

- Phase name, illumination, cycle angle and geometric phase angle.
- Apparent topocentric Moon altitude, azimuth, distance, Sun altitude and Moon/Sun separation.
- Last/next new moon, next first quarter, full moon and last quarter, and current lunation length.
- **Next moonrise and next moonset**, using the newer local implementation now included in the public template.
- Above-horizon state, clear-sky visibility estimate, full-moon status and rough possible-eclipse flag.
- Home Assistant entities, uptime, version, status and safe-mode restart button.

SNTP time is preferred, with Home Assistant time as fallback. Without a valid clock the script returns without publishing new calculations. Updates run on time synchronization and every 15 minutes. Local computation can continue while HA is unreachable after a usable clock is established; networking is still needed to acquire/synchronize time.

See [calculation behavior and limits](docs/CALCULATIONS.md). “Visible Clear Sky” is a geometry/brightness heuristic; it does not measure clouds. The eclipse flag is not a prediction of an observable eclipse.

## Set up a Wi-Fi build

1. Keep `moon_node.yaml` and `moon_node_wifi.example.yaml` together. Copy the example to **`moon_node_wifi.local.yaml`**; this private filename is ignored by Git.
2. Copy `secrets.example.yaml` to **`secrets.yaml`** in the same directory. Replace every placeholder with your own credentials and observer latitude, longitude and elevation. North/east are positive; west/south are negative. The public base's `0,0` values are placeholders.
3. Generate a unique API key using the [ESPHome API key generator](https://esphome.io/components/api/) or `openssl rand -base64 32`. Supply your own OTA password and network credentials in the private secrets file.
4. Review the **hardware requirements below**. The base retains the original node's board-specific advanced settings.
5. Validate and compile your private wrapper:

   ```bash
   esphome config moon_node_wifi.local.yaml
   esphome compile moon_node_wifi.local.yaml
   ```

6. Use your board's normal ESPHome installation process. Before OTA to an existing device, confirm chip revision and bootloader compatibility. Add the device in Home Assistant using your API key, then check fresh values.

`moon_node.yaml` is the calculation base package. It intentionally has no network transport and is not the standalone file to validate/flash unchanged. The Wi-Fi wrapper supplies networking and location substitutions through [ESPHome packages](https://esphome.io/components/packages/). An Ethernet build can supply its own wrapper.

## Hardware requirements

The original target is `esp32dev`, original ESP32, ESP-IDF. Its retained configuration requires **chip revision 3.1 or newer** and enables **`sram1_as_iram`**, which requires a compatible bootloader. These settings were specific to the original node. Check the [official ESP32 configuration documentation](https://esphome.io/components/esp32/) and your actual board before building. If needed, adjust the advanced block in your local copy and validate for that hardware. Repository checks do not flash a device.

The configured ESPHome minimum is 2026.4.0. The Wi-Fi example was schema-validated and C++ source-generated using **ESPHome 2026.9.1** with synthetic settings; see [validation](docs/VALIDATION.md) for exact scope. This does not establish a completed hardware or accuracy test on every board/version.

## Home Assistant and displays

The node publishes sensor, binary-sensor and timestamp text entities through the encrypted ESPHome API. Rise/set and phase-event timestamps are UTC ISO strings; HA may display them in its own timezone. Use the entity IDs created in your installation.

Rise/set searches 72 hours ahead and caches results between updates. An `unknown` value means no crossing was found within that window, which can occur at high latitudes. Existing phase names and full-moon status use a broad event window rather than an instantaneous transition.

Planned work includes round/rectangular display drivers, Moon rendering, weather-aware visibility, broader reference comparisons and hardware timing/memory measurements. See [CHANGELOG.md](CHANGELOG.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## Privacy

Keep `secrets.yaml` and `*.local.yaml` private. Do not upload credentials, precise household coordinates, device identities, logs containing addresses or identifying dashboard screenshots. Only placeholders and public/synthetic test locations belong here.

## License

MIT — see [LICENSE](LICENSE).

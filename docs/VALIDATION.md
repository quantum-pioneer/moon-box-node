# Software validation — October 23, 2026

This public update promotes the newer local moonrise/moonset code. Existing phase and visibility mathematics were retained. Private location values and unrelated device features were not copied.

## Checks completed

- **ESPHome 2026.9.1 schema validation:** the Wi-Fi package wrapper passed with synthetic credentials and observer settings in a separate temporary copy.
- **ESPHome C++ generation:** `compile --only-generate` completed. The generated source contained both new timestamp entities and the wrapper's synthetic latitude, longitude and elevation overrides.
- **Six exact-lambda host tests passed:** the harness extracts the actual YAML calculation, supplies fake ESPHome clock/entities and replaces only observer substitutions. It compiles with C++17 and tests finite/range invariants, invalid-time behavior, HA fallback, SNTP precedence, short-interval cached results, event rollover, backward-clock refresh and limited reference samples. Normal, equatorial and high-latitude samples exercise future events and bounded-search `unknown` results.
- **Publication review:** no real credentials, household coordinates, network/device identities, unrelated features or machine paths were included. API/OTA use private secret references; public examples contain placeholders.

Run the host checks with Python 3, PyYAML and a C++17 `g++` compiler:

```bash
python3 -m unittest discover -s tests -v
```

The extracted calculation's SHA-256 was `69b7f8e5da08faf1279ad562587b3fdd57648f7e588b4e76a9424903b691493c`. The YAML loader in the tests treats `!secret` references as inert names; it does not read private secrets.

## Limited public-reference comparison

The test fixture records three public date/location samples from the [US Naval Observatory API](https://aa.usno.navy.mil/data/api), with timezone offset 0 and elevation 0. These are public test coordinates, not a household location. Six rise/set predictions had a maximum absolute offset of **43 seconds from the published reference minute**, within the explicit 120-second smoke-test tolerance.

| Sample / date | Predicted rise / set | USNO rise / set |
|---|---|---|
| Washington DC area, 38.9° N / 77.0° W, 2026-10-23 | 20:48:01 / 08:32:11 | 20:48 / 08:32 |
| Same coordinates, 2026-10-24 | 21:13:08 / 09:39:39 | 21:13 / 09:39 |
| Equator, 0° / 0°, 2026-10-23 | 15:39:17 / 03:16:25 | 15:40 / 03:16 |

All times are on the listed date in UTC; references use their documented UT/timezone conventions and publish minute precision. Comparing a second-valued prediction to a reference minute does not measure true second-level error. Fixture source URLs and assumptions are included in `tests/fixtures/usno_moonrise_set_samples.json`. These samples are a limited regression check, not a general accuracy guarantee.

## Limits

Source generation is not an ESP32 target firmware build. No physical device was flashed or measured by this update. Display hardware, ESP32 search runtime/stack/watchdog behavior, long-term operation and broad astronomical accuracy remain unvalidated. Host invariants do not prove event-time accuracy. See [CALCULATIONS.md](CALCULATIONS.md) for horizon, atmosphere, high-latitude and search-window limitations.

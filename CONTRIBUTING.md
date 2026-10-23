# Contributing

Issues and pull requests are welcome for calculation comparisons, display hardware, setup problems and practical improvements.

For a calculation discrepancy, include the exact UTC input time, software commit, field/units, reference provider and its horizon/refraction/time conventions. Use a public or synthetic location instead of household coordinates. State whether results came from a host harness, ESPHome build or physical hardware.

For a setup problem, include ESPHome version, board/chip revision, framework, bootloader compatibility, whether the Wi-Fi wrapper was used, and a small redacted error excerpt. Do not post secrets, network/device identities or a full home configuration.

The goal is a physical Moon Box, but display drivers and weather-aware visibility remain planned. Label untested ideas clearly. A compile or host test is not proof of astronomical accuracy or a successful physical installation.

Keep verification focused on the behavior changed. Preserve the distinction between observer-independent phases and observer-dependent horizon/position calculations. Explain changes to thresholds, atmospheric assumptions, search bounds or cache behavior.

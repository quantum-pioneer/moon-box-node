# Calculation behavior and limits

The YAML update script calculates locally; it does not call an astronomy web service. Its phase-event series and lunar-position tables are identified in source as Meeus chapters 49 and 47. A solar approximation, observer-centered parallax and standard atmospheric refraction supply local geometry.

## Existing outputs

- **Moon Altitude** is apparent topocentric center altitude after modeled refraction; azimuth is observer-centered.
- **Moon Phase Angle** is 0–360° progression based on age/current lunation length. **Moon Phase Angle Geometric** is a different illumination-related angle.
- **Moon Above Horizon** uses apparent center altitude plus semidiameter: an upper-limb horizon criterion in this model.
- **Moon Visible Clear Sky** applies altitude, illumination, Sun separation and Sun-altitude thresholds. It does not observe clouds, haze, obstructions or sky brightness.
- **Moon Phase** labels an event within a ±18-hour window; **Moon Is Full** similarly uses an 18-hour window around full moon. Labels differ from exact event timestamps.
- **Eclipse Possible at Next Full** is a rough lunar-node-angle threshold. It does not determine eclipse magnitude, contact times, type or local visibility.
- Phase-event timestamps use a modeled TT-to-UT correction. The source labels its ΔT polynomial for 2005–2050; broad accuracy outside that span is not claimed.

## Next moonrise / moonset

The newer local implementation evaluates trial UTC Julian dates using the same lunar terms, parallax, refraction and semidiameter rule. It searches 72 hours ahead in 10-minute steps and refines sign changes with 24 bisections. Results cache for up to 15 minutes, with refresh after an event passes or the clock moves backward by more than 60 seconds.

Outputs are UTC ISO strings. `unknown` means no crossing was found within the search window. High-latitude crossings can be absent for days; an endpoint sign-change scan can miss a grazing rise/set pair entirely inside one interval. Bisection precision does not establish subsecond physical accuracy.

Standard refraction is approximate. Elevation affects parallax, but terrain, obstructions and a full horizon-dip model are not supplied. Compare reference results with matching definitions, elevation and timezone. [USNO explains rise/set conventions and observational limits](https://aa.usno.navy.mil/faq/RST_defs).

Worst-case search performs hundreds of synchronous trial evaluations. ESP32 execution time, stack/heap and watchdog behavior still need measurement. Host checks, limited reference samples and ESPHome generation are listed in [VALIDATION.md](VALIDATION.md); they do not establish a finished display or uniform ephemeris accuracy.

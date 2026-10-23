#!/usr/bin/env python3
"""Host checks of the exact YAML lambda using synthetic ESPHome time/entity stubs.

Requires Python 3, PyYAML and g++ with C++17. This validates runtime invariants,
not independent astronomical accuracy, ESPHome target compilation or hardware.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "moon_node.yaml"


def utc(text):
    return int(datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp())


def lambda_source():
    class TemplateLoader(yaml.SafeLoader):
        pass

    # Preserve secret names as inert text; never read a secrets file.
    TemplateLoader.add_constructor("!secret", lambda loader, node: loader.construct_scalar(node))
    doc = yaml.load(YAML_PATH.read_text(), Loader=TemplateLoader)
    script = next(x for x in doc["script"] if x["id"] == "update_moon_entities")
    actions = script["then"]
    return next(x["lambda"] for x in actions if "lambda" in x)


def harness_source(raw):
    names = sorted(set(re.findall(r"\bid\((\w+)\)", raw)) - {"moon_time", "ha_time"})
    # Only public observer substitutions are replaced; raw astronomy code is unchanged.
    code = raw
    for name in ("latitude", "longitude", "elevation_m"):
        code = code.replace("${observer_" + name + "}", "test_observer_" + name)
    if "${" in code:
        raise ValueError("Unexpected unresolved ESPHome substitution")
    prefix = r'''
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>
struct ESPTime {
  int64_t timestamp = 0;
  bool valid = false;
  bool is_valid() const { return valid; }
};
struct TestClock {
  ESPTime value;
  ESPTime now() const { return value; }
};
struct Entity {
  size_t calls = 0;
  std::string state = "null";
  void publish_state(const std::string &x) { ++calls; state = "\"" + x + "\""; }
  void publish_state(const char *x) { publish_state(std::string(x)); }
  void publish_state(bool x) { ++calls; state = x ? "true" : "false"; }
  template<class T, typename = std::enable_if_t<std::is_arithmetic_v<T> && !std::is_same_v<T, bool>>>
  void publish_state(T x) {
    ++calls;
    if (!std::isfinite(double(x))) { state = "null"; return; }
    std::ostringstream out; out << std::setprecision(17) << x; state = out.str();
  }
};
TestClock moon_time, ha_time;
double test_observer_latitude = 0.0, test_observer_longitude = 0.0, test_observer_elevation_m = 0.0;
#define id(x) x
'''
    declarations = "\n".join("Entity " + x + ";" for x in names)
    function = "\nvoid update_moon_entities() {\n" + code + "\n}\n"
    output = "\n".join(
        'std::cout << ",\\\"' + x + '\\\":" << ' + x + '.state;'
        for x in names
    )
    calls = " + ".join(x + ".calls" for x in names)
    main = r'''
int main(int argc, char **argv) {
  if (argc < 5) return 2;
  test_observer_latitude = std::stod(argv[1]);
  test_observer_longitude = std::stod(argv[2]);
  test_observer_elevation_m = std::stod(argv[3]);
  for (int arg = 4; arg < argc; ++arg) {
    std::string event(argv[arg]);
    std::replace(event.begin(), event.end(), ',', ' ');
    std::istringstream in(event);
    int sntp_valid, ha_valid;
    if (!(in >> moon_time.value.timestamp >> sntp_valid >> ha_time.value.timestamp >> ha_valid)) return 3;
    moon_time.value.valid = sntp_valid; ha_time.value.valid = ha_valid;
    auto before = CALLS;
    update_moon_entities();
    auto after = CALLS;
    std::cout << "{\"published\":" << (after - before);
    OUTPUT
    std::cout << "}\n";
  }
}
'''.replace("CALLS", calls).replace("OUTPUT", output)
    return prefix + declarations + function + main


class MoonLambdaHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="moon-lambda-host-")
        cls.directory = Path(cls.temp.name)
        cls.raw = lambda_source()
        cls.lambda_sha256 = hashlib.sha256(cls.raw.encode()).hexdigest()
        cpp = cls.directory / "moon_lambda.cpp"
        cpp.write_text(harness_source(cls.raw))
        cls.executable = cls.directory / "moon_lambda"
        compile_result = subprocess.run(
            ["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", str(cpp), "-o", str(cls.executable)],
            capture_output=True, text=True,
        )
        if compile_result.returncode:
            raise RuntimeError(compile_result.stdout + compile_result.stderr)
        cls.compile_diagnostics = compile_result.stderr
        print("exact_lambda_sha256=" + cls.lambda_sha256)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_events(self, latitude, longitude, elevation, events):
        args = [str(self.executable), str(latitude), str(longitude), str(elevation)]
        args += [",".join(str(int(x)) for x in event) for event in events]
        result = subprocess.run(args, check=True, capture_output=True, text=True, timeout=20)
        return [json.loads(x) for x in result.stdout.splitlines()]

    def validate_states(self, state, timestamp):
        self.assertGreater(state["published"], 0)
        for key in ("moon_altitude", "moon_azimuth", "sun_altitude", "moon_distance_km", "moon_illumination"):
            self.assertIsInstance(state[key], (int, float))
            self.assertTrue(math.isfinite(state[key]), key)
        self.assertGreaterEqual(state["moon_azimuth"], 0)
        self.assertLess(state["moon_azimuth"], 360)
        self.assertGreaterEqual(state["moon_illumination"], 0)
        self.assertLessEqual(state["moon_illumination"], 100)
        self.assertGreater(state["moon_distance_km"], 330000)
        self.assertLess(state["moon_distance_km"], 410000)
        for key in ("next_moonrise", "next_moonset"):
            if state[key] != "unknown":
                event = utc(state[key])
                self.assertGreaterEqual(event, timestamp)
                self.assertLessEqual(event, timestamp + 72 * 3600 + 1)
                self.assertTrue(state[key].endswith("+00:00"))
        return state

    def test_normal_equatorial_and_high_latitude_samples(self):
        for lat, lon, elev, iso in (
            (40.7128, -74.0060, 10, "2026-10-23T12:00:00Z"),
            (0, 0, 0, "2026-10-23T00:00:00Z"),
            (69.6492, 18.9553, 0, "2026-06-21T00:00:00Z"),
            (89.0, 0, 0, "2026-10-23T00:00:00Z"),
            (-69.6492, 18.9553, 0, "2026-12-21T00:00:00Z"),
        ):
            with self.subTest(latitude=lat, date=iso):
                t = utc(iso)
                state = self.run_events(lat, lon, elev, [(t, 1, 0, 0)])[0]
                self.validate_states(state, t)
                if abs(lat) < 60:
                    self.assertNotEqual(state["next_moonrise"], "unknown")
                    self.assertNotEqual(state["next_moonset"], "unknown")
                print(json.dumps({"sample": [lat, lon, elev, iso], "next_moonrise": state["next_moonrise"], "next_moonset": state["next_moonset"]}))

    def test_invalid_clocks_publish_nothing_and_preserve_previous_states(self):
        t = utc("2026-10-23T12:00:00Z")
        states = self.run_events(40.7128, -74.0060, 10, [(t, 0, t, 0), (t, 1, 0, 0), (t + 60, 0, t + 60, 0)])
        self.assertEqual(states[0]["published"], 0)
        self.assertIsNone(states[0]["next_moonrise"])
        self.assertEqual(states[2]["published"], 0)
        for name in states[1]:
            if name != "published":
                self.assertEqual(states[1][name], states[2][name], name)

    def test_ha_fallback_and_sntp_precedence(self):
        t = utc("2026-10-23T12:00:00Z")
        baseline = self.run_events(40.7128, -74.0060, 10, [(t, 1, 0, 0)])[0]
        fallback = self.run_events(40.7128, -74.0060, 10, [(0, 0, t, 1)])[0]
        precedence = self.run_events(40.7128, -74.0060, 10, [(t, 1, t + 86400, 1)])[0]
        self.assertEqual(baseline, fallback)
        self.assertEqual(baseline, precedence)

    def test_cached_outputs_and_event_rollover(self):
        t = utc("2026-10-23T12:00:00Z")
        initial = self.run_events(40.7128, -74.0060, 10, [(t, 1, 0, 0)])[0]
        first_event = min(utc(initial[name]) for name in ("next_moonrise", "next_moonset"))
        states = self.run_events(40.7128, -74.0060, 10, [(t, 1, 0, 0), (t + 60, 1, 0, 0), (t + 901, 1, 0, 0), (first_event + 1, 1, 0, 0)])
        self.assertEqual(states[0]["next_moonrise"], states[1]["next_moonrise"])
        self.assertEqual(states[0]["next_moonset"], states[1]["next_moonset"])
        self.assertNotEqual(states[0]["moon_altitude"], states[1]["moon_altitude"])
        self.validate_states(states[2], t + 901)
        self.validate_states(states[3], first_event + 1)
        due_name = min(("next_moonrise", "next_moonset"), key=lambda name: utc(initial[name]))
        self.assertGreater(utc(states[3][due_name]), first_event + 1)
        fresh = self.run_events(40.7128, -74.0060, 10, [(first_event + 1, 1, 0, 0)])[0]
        self.assertEqual(states[3], fresh)

    def test_limited_usno_public_coordinate_reference_samples(self):
        # Six events at two public coordinates over three date/location cases.
        # USNO publishes minutes: this tolerance is a smoke check, not a claim
        # of second-resolution reference truth or worldwide/year-round accuracy.
        fixture = json.loads((ROOT / "tests/fixtures/usno_moonrise_set_samples.json").read_text())
        tolerance = fixture["maximum_absolute_difference_seconds"]
        for sample in fixture["samples"]:
            with self.subTest(sample=sample["id"]):
                t = utc(sample["start_utc"])
                state = self.run_events(sample["latitude_deg"], sample["longitude_deg"], sample["elevation_m"], [(t, 1, 0, 0)])[0]
                self.validate_states(state, t)
                for name in ("next_moonrise", "next_moonset"):
                    self.assertNotEqual(state[name], "unknown")
                    difference = utc(state[name]) - utc(sample[name + "_utc"])
                    self.assertLessEqual(abs(difference), tolerance, sample["id"] + ":" + name)
                    print(json.dumps({"reference_sample": sample["id"], "event": name, "predicted_utc": state[name], "reference_utc": sample[name + "_utc"], "difference_from_published_minute_seconds": difference}))

    def test_backward_clock_jump_refresh_matches_fresh_process(self):
        t = utc("2026-10-23T12:00:00Z")
        states = self.run_events(40.7128, -74.0060, 10, [(t, 1, 0, 0), (t - 86400, 1, 0, 0)])
        fresh = self.run_events(40.7128, -74.0060, 10, [(t - 86400, 1, 0, 0)])[0]
        self.assertEqual(states[1], fresh)
        self.assertNotEqual(states[0]["next_moonrise"], states[1]["next_moonrise"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

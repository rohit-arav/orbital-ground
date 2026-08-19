# Orbital Ground

`orbital-ground` is a modular control plane for a learning-focused RF ground station. Phase 1
targets an RTL-SDR Blog V3, its dipole kit, and Meteor-M LRPT weather imagery. The design keeps
radio capture, orbit prediction, processing, and observation storage separate so the station can
later gain a filtered LNA, QFH/turnstile antenna, antenna rotator, better SDRs, and new science
pipelines without a rewrite.

> Receive only. Check the radio regulations that apply at your location before adding any
> transmitting hardware.

## What works in Phase 1

- Fetch current weather-satellite TLEs from CelesTrak.
- Predict Meteor M2-3 and M2-4 passes above a configurable elevation mask.
- Record bounded unsigned 8-bit IQ captures using `rtl_sdr`.
- Process a recording with SatDump's `meteor_m2-x_lrpt` pipeline.
- Store every observation in its own directory with reproducibility metadata.
- Preview hardware commands using `--dry-run` without an SDR attached.

Meteor transmitter status and frequencies can change. The example configuration uses M2-3 at
137.9 MHz and M2-4 at 137.1 MHz, but verify current status before scheduling.

## Install

Requirements:

- Python 3.11+
- RTL-SDR command-line tools (`rtl_sdr` on `PATH`)
- [SatDump](https://www.satdump.org/) (`satdump` on `PATH`)



### Windows

Make sure the RTL-SDR uses a WinUSB driver (commonly installed with Zadig). Then:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item config\station.example.toml config\station.toml
```

The project installs the IANA `tzdata` package automatically on Windows so names such as
`America/Los_Angeles` work with Python's cross-platform timezone API.

Edit `config/station.toml` with your approximate latitude, longitude, altitude, and timezone. The
station file is intentionally not created automatically: pass predictions are meaningless until
the location is correct.

### macOS

Install Python and the RTL-SDR command-line tools with Homebrew, then install this project:

```bash
xcode-select --install
brew install python librtlsdr
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
cp config/station.example.toml config/station.toml
```

Download the macOS SatDump release and drag `SatDump.app` into `/Applications`. The code
automatically checks `/Applications/SatDump.app/Contents/MacOS/satdump`, Apple Silicon Homebrew's
`/opt/homebrew/bin`, Intel Homebrew's `/usr/local/bin`, and the normal `PATH`. An explicit path in
`config/station.toml` still takes precedence.

macOS generally exposes the RTL-SDR through libusb without Zadig or a Linux-style kernel-driver
change. Test it with `rtl_test`, stop with Control-C, and then run `groundstation doctor`.

## First session

```powershell
# Check configuration and find the RTL-SDR and SatDump executables.
groundstation doctor

# Fetch orbital elements, then list the next 24 hours of usable passes.
groundstation update-tle
groundstation passes --hours 24

# Verify the exact capture and decode commands without touching hardware.
groundstation record "METEOR-M2 4" --seconds 30 --decode --dry-run

# During a pass, record and process ten minutes.
groundstation record "METEOR-M2 4" --seconds 600 --decode
```

The `groundstation` commands are identical on macOS after `source .venv/bin/activate`. PowerShell
examples use backslashes only for environment setup; station behavior and observation formats are
portable across both systems.

Raw `baseband.cu8`, `metadata.json`, and SatDump output are placed under `data/observations/`.
A 1.024 MS/s capture consumes about 2 MiB/s (roughly 1.2 GiB for ten minutes), so watch disk
space. Keeping the raw IQ is valuable while learning; it allows repeated decoding without waiting
for another pass.

## Antenna setup for 137 MHz

Start simple and change one variable at a time:

1. Extend each telescoping dipole leg to about 53–55 cm (approximately a quarter wavelength).
2. Arrange the elements as a horizontal V, roughly 120° apart, with the feed point elevated and a
  clear view of the sky.
3. Begin with passes above 30°. Once reception is repeatable, lower the elevation mask.
4. Tune gain experimentally. Maximum RTL-SDR gain is often worse in RF-noisy locations.
5. Use a short USB extension to move the SDR away from the computer and its noise.

The stock dipole is linearly polarized while Meteor LRPT is circularly polarized, so fades are
normal. A 137 MHz QFH or turnstile antenna is the highest-value early antenna upgrade. A 137 MHz
band-pass filter and low-noise amplifier become useful after the antenna and feed line are sound.

## Architecture

```text
TLE provider -> pass predictor -> scheduler (next phase)
                       |                |
                       v                v
                  station model -> radio driver -> raw observation
                                                    |
                                                    v
                                            SatDump processor
                                                    |
                                                    v
                                        imagery + science products
```

The core types live in `models.py`; external programs are isolated in `drivers.py`. Future radio,
rotator, and decoder backends should implement the same boundary rather than leaking tool-specific
commands into scheduling logic.

## Roadmap

- **Phase 1:** manual fixed-antenna Meteor passes, repeatable raw capture, SatDump processing.
- **Phase 2:** unattended scheduler, Doppler correction, observation database, notifications.
- **Phase 3:** QFH/turnstile, filtered LNA, calibrated signal-quality metrics, system health.
- **Phase 4:** azimuth/elevation rotator and higher-rate VHF/L-band receivers.
- **Phase 5:** multi-mission science archive, provenance, calibration, visualization, and export.

Do not automate unattended captures until manual runs are reliable. A scheduler amplifies both a
working setup and a bad configuration.

## Development

```powershell
pytest
ruff check .
```

The test suite does not require an SDR or network connection.
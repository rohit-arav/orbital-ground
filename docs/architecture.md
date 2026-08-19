# Architecture decisions

## Raw observations are immutable

Each reception creates a unique UTC-stamped directory. Capture data and initial metadata are the
source record; processing creates derived products. Future calibration and decoding versions can
therefore be compared against the same RF observation.

## Hardware and processors are adapters

Orbit and station logic must not depend on RTL-SDR or SatDump command syntax. Today the adapters
invoke local command-line programs. They can later be replaced with SoapySDR, a network radio,
SatDump live mode, or a job service without changing pass models.

## Configuration is data

Station coordinates, downlinks, gain, and pipeline choices live in TOML rather than source code.
Satellite transmission state is deliberately not treated as permanent truth. A future catalog
provider can update it independently of orbital elements.

## Planned service boundaries

- **Catalog:** spacecraft identity, downlinks, modes, and operational status.
- **Orbit:** TLE/OMM acquisition, freshness, propagation, and pass events.
- **Radio:** capability discovery, tuning, sampling, and health.
- **Pointing:** fixed antenna now; rotator trajectory later.
- **Scheduler:** resource-aware observation plans and recovery.
- **Processor:** SatDump initially; versioned pipelines and calibration later.
- **Archive:** immutable observations, derived products, provenance, search, and retention.


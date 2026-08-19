from __future__ import annotations

import json
import subprocess
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from .executables import resolve_executable
from .models import Decoder, Observation, Radio, Satellite


def observation_id(satellite: Satellite, when: datetime) -> str:
    slug = satellite.name.lower().replace(" ", "-")
    return f"{when.astimezone(UTC):%Y%m%dT%H%M%SZ}_{slug}"


def prepare_observation(
    root: Path, satellite: Satellite, duration: int, radio: Radio
) -> Observation:
    started = datetime.now(UTC)
    obs_id = observation_id(satellite, started)
    directory = root / obs_id
    directory.mkdir(parents=True, exist_ok=False)
    observation = Observation(
        obs_id, satellite, started, duration, satellite.downlink_hz, radio.sample_rate_hz, directory
    )
    metadata = asdict(observation)
    metadata["started_at"] = started.isoformat()
    metadata["directory"] = str(directory)
    metadata["satellite"] = asdict(satellite)
    (directory / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return observation


def rtl_sdr_command(radio: Radio, observation: Observation) -> list[str]:
    sample_count = observation.duration_seconds * radio.sample_rate_hz
    return [
        "rtl_sdr",
        "-d",
        radio.device,
        "-f",
        str(observation.center_frequency_hz),
        "-s",
        str(radio.sample_rate_hz),
        "-g",
        str(radio.gain_db),
        "-p",
        str(radio.ppm),
        "-n",
        str(sample_count),
        str(observation.directory / "baseband.cu8"),
    ]


def capture(radio: Radio, observation: Observation, dry_run: bool = False) -> list[str]:
    command = rtl_sdr_command(radio, observation)
    if not dry_run:
        executable = resolve_executable(command[0])
        if executable is None:
            raise RuntimeError("rtl_sdr was not found on PATH; install rtl-sdr tools")
        command[0] = executable
        subprocess.run(command, check=True)
    return command


def satdump_command(decoder: Decoder, observation: Observation) -> list[str]:
    satellite_number = observation.satellite.name.removeprefix("METEOR-").replace(" ", "-")
    return [
        decoder.executable,
        "pipeline",
        decoder.pipeline,
        decoder.input_level,
        str(observation.directory / "baseband.cu8"),
        str(observation.directory / "products"),
        "--samplerate",
        str(observation.sample_rate_hz),
        "--baseband_format",
        "u8",
        "--satellite_number",
        satellite_number,
    ]


def decode(decoder: Decoder, observation: Observation, dry_run: bool = False) -> list[str]:
    command = satdump_command(decoder, observation)
    if not dry_run:
        executable = resolve_executable(command[0])
        if executable is None:
            raise RuntimeError("SatDump was not found on PATH")
        command[0] = executable
        subprocess.run(command, check=True)
    return command

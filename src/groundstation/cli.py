from __future__ import annotations

import argparse
import shlex
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import AppConfig, load_config
from .drivers import capture, decode, prepare_observation
from .executables import resolve_executable
from .predict import load_satellites, predict_passes
from .tle import is_fresh, update_tle


def _config(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default="config/station.toml", help="station TOML file")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="groundstation", description="RF ground-station control")
    commands = root.add_subparsers(dest="command", required=True)
    status = commands.add_parser("doctor", help="validate configuration and external tools")
    _config(status)
    tle = commands.add_parser("update-tle", help="download fresh orbital elements")
    _config(tle)
    passes = commands.add_parser("passes", help="show upcoming usable passes")
    _config(passes)
    passes.add_argument("--hours", type=float, default=24)
    record = commands.add_parser("record", help="capture one satellite to an observation folder")
    _config(record)
    record.add_argument("satellite", help="satellite name or NORAD ID")
    record.add_argument("--seconds", type=int, required=True)
    record.add_argument("--decode", action="store_true")
    record.add_argument("--dry-run", action="store_true")
    return root


def _find_satellite(config: AppConfig, query: str):
    for satellite in config.satellites:
        if query.casefold() == satellite.name.casefold() or query == str(satellite.norad_id):
            return satellite
    raise ValueError(f"unknown satellite: {query}")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "doctor":
            import platform

            print(f"configuration: OK ({config.source_path})")
            print(f"platform: {platform.system()} {platform.machine()}")
            print(
                f"station: {config.station.name} ({config.station.latitude_deg:.4f}, "
                f"{config.station.longitude_deg:.4f})"
            )
            print(
                f"TLE cache: {'fresh' if is_fresh(config.tle_file, config.tle_max_age_hours) else 'missing/stale'}"
            )
            for tool in ("rtl_sdr", config.decoder.executable):
                print(f"{tool}: {resolve_executable(tool) or 'NOT FOUND'}")
        elif args.command == "update-tle":
            print(update_tle(config.tle_url, config.tle_file))
        elif args.command == "passes":
            if not is_fresh(config.tle_file, config.tle_max_age_hours):
                update_tle(config.tle_url, config.tle_file)
            orbiters = load_satellites(config.tle_file, config.satellites)
            try:
                local_tz = ZoneInfo(config.station.timezone)
            except ZoneInfoNotFoundError as error:
                raise ValueError(
                    f"unknown timezone {config.station.timezone!r}; "
                    "on Windows, reinstall the project to install tzdata"
                ) from error
            for item in predict_passes(
                config.station, config.satellites, orbiters, hours=args.hours
            ):
                print(
                    f"{item.aos.astimezone(local_tz):%Y-%m-%d %H:%M:%S %Z}  "
                    f"{item.satellite.name:<12} max {item.max_elevation_deg:5.1f} deg  "
                    f"{item.duration_seconds // 60:2d}m {item.duration_seconds % 60:02d}s  "
                    f"{item.aos_azimuth_deg:03.0f}->{item.los_azimuth_deg:03.0f} deg"
                )
        elif args.command == "record":
            if args.seconds <= 0:
                raise ValueError("--seconds must be positive")
            satellite = _find_satellite(config, args.satellite)
            observation = prepare_observation(
                config.storage_root, satellite, args.seconds, config.radio
            )
            command = capture(config.radio, observation, args.dry_run)
            print("capture:", shlex.join(command))
            if args.decode:
                command = decode(config.decoder, observation, args.dry_run)
                print("decode:", shlex.join(command))
            print("observation:", observation.directory)
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

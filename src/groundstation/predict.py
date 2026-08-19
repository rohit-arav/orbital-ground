from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from skyfield.api import EarthSatellite, load, wgs84

from .models import Pass, Satellite, Station


def load_satellites(path: Path, wanted: tuple[Satellite, ...]) -> dict[int, EarthSatellite]:
    by_id = {sat.norad_id: sat for sat in wanted if sat.enabled}
    result: dict[int, EarthSatellite] = {}
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for index in range(len(lines) - 2):
        if lines[index + 1].startswith("1 ") and lines[index + 2].startswith("2 "):
            try:
                norad_id = int(lines[index + 1][2:7])
            except ValueError:
                continue
            if norad_id in by_id:
                result[norad_id] = EarthSatellite(lines[index + 1], lines[index + 2], lines[index])
    missing = sorted(set(by_id) - set(result))
    if missing:
        raise ValueError(f"TLE file is missing NORAD IDs: {missing}")
    return result


def predict_passes(
    station: Station,
    configured: tuple[Satellite, ...],
    orbiters: dict[int, EarthSatellite],
    start: datetime | None = None,
    hours: float = 24,
) -> list[Pass]:
    start = start or datetime.now(UTC)
    if start.tzinfo is None:
        raise ValueError("prediction start must be timezone-aware")
    end = start + timedelta(hours=hours)
    ts = load.timescale()
    observer = wgs84.latlon(station.latitude_deg, station.longitude_deg, station.altitude_m)
    configured_by_id = {item.norad_id: item for item in configured}
    passes: list[Pass] = []
    for norad_id, orbiter in orbiters.items():
        times, events = orbiter.find_events(
            observer,
            ts.from_datetime(start),
            ts.from_datetime(end),
            altitude_degrees=station.min_elevation_deg,
        )
        pending: dict[int, tuple[datetime, float]] = {}
        for time, event in zip(times, events, strict=True):
            moment = time.utc_datetime()
            alt, az, _ = (orbiter - observer).at(time).altaz()
            if event == 0:
                pending[0] = (moment, az.degrees)
            elif event == 1 and 0 in pending:
                pending[1] = (moment, alt.degrees)
            elif event == 2 and 0 in pending and 1 in pending:
                passes.append(
                    Pass(
                        configured_by_id[norad_id],
                        pending[0][0],
                        pending[1][0],
                        moment,
                        pending[1][1],
                        pending[0][1],
                        az.degrees,
                    )
                )
                pending = {}
    return sorted(passes, key=lambda item: item.aos)

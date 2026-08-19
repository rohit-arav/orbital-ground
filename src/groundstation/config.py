from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from .models import Decoder, Radio, Satellite, Station


@dataclass(frozen=True)
class AppConfig:
    station: Station
    radio: Radio
    decoder: Decoder
    satellites: tuple[Satellite, ...]
    storage_root: Path
    tle_file: Path
    tle_url: str
    tle_max_age_hours: int
    source_path: Path


def load_config(path: str | Path) -> AppConfig:
    source = Path(path).resolve()
    with source.open("rb") as handle:
        raw = tomllib.load(handle)
    base = source.parent.parent if source.parent.name == "config" else source.parent
    station = Station(**raw["station"])
    radio = Radio(**raw["radio"])
    decoder = Decoder(**raw["decoder"])
    satellites = tuple(Satellite(**item) for item in raw.get("satellites", []))
    if not satellites:
        raise ValueError("configure at least one satellite")
    return AppConfig(
        station=station,
        radio=radio,
        decoder=decoder,
        satellites=satellites,
        storage_root=(base / raw["storage"]["root"]).resolve(),
        tle_file=(base / raw["storage"]["tle_file"]).resolve(),
        tle_url=raw["tle"]["url"],
        tle_max_age_hours=int(raw["tle"]["max_age_hours"]),
        source_path=source,
    )

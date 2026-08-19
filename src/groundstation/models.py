from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Station:
    name: str
    latitude_deg: float
    longitude_deg: float
    altitude_m: float
    timezone: str
    min_elevation_deg: float

    def __post_init__(self) -> None:
        if not -90 <= self.latitude_deg <= 90:
            raise ValueError("station latitude must be between -90 and 90")
        if not -180 <= self.longitude_deg <= 180:
            raise ValueError("station longitude must be between -180 and 180")
        if not 0 <= self.min_elevation_deg < 90:
            raise ValueError("minimum elevation must be in [0, 90)")


@dataclass(frozen=True)
class Satellite:
    name: str
    norad_id: int
    downlink_hz: int
    mode: str
    enabled: bool = True


@dataclass(frozen=True)
class Radio:
    driver: str
    device: str
    sample_rate_hz: int
    gain_db: float
    ppm: int
    bias_tee: bool


@dataclass(frozen=True)
class Decoder:
    driver: str
    executable: str
    pipeline: str
    input_level: str


@dataclass(frozen=True)
class Pass:
    satellite: Satellite
    aos: datetime
    culmination: datetime
    los: datetime
    max_elevation_deg: float
    aos_azimuth_deg: float
    los_azimuth_deg: float

    @property
    def duration_seconds(self) -> int:
        return round((self.los - self.aos).total_seconds())


@dataclass(frozen=True)
class Observation:
    observation_id: str
    satellite: Satellite
    started_at: datetime
    duration_seconds: int
    center_frequency_hz: int
    sample_rate_hz: int
    directory: Path

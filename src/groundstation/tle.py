from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen


def is_fresh(path: Path, max_age_hours: int) -> bool:
    if not path.exists():
        return False
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    return datetime.now(UTC) - modified < timedelta(hours=max_age_hours)


def update_tle(url: str, destination: Path, timeout: int = 30) -> Path:
    request = Request(url, headers={"User-Agent": "orbital-ground/0.1"})
    with urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    _validate(payload)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(destination)
    return destination


def _validate(payload: str) -> None:
    lines = [line.strip() for line in payload.splitlines() if line.strip()]
    if len(lines) < 3 or not any(line.startswith("1 ") for line in lines):
        raise ValueError("download did not contain valid-looking TLE data")

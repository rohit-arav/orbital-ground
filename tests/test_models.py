from datetime import UTC, datetime, timedelta

import pytest

from groundstation.models import Pass, Satellite, Station


def test_station_rejects_invalid_location():
    with pytest.raises(ValueError):
        Station("bad", 91, 0, 0, "UTC", 10)


def test_pass_duration():
    start = datetime.now(UTC)
    satellite = Satellite("test", 1, 100, "test")
    item = Pass(
        satellite, start, start + timedelta(minutes=4), start + timedelta(minutes=9), 45, 10, 190
    )
    assert item.duration_seconds == 540

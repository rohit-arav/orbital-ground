from datetime import UTC, datetime
from pathlib import Path

from groundstation.drivers import rtl_sdr_command, satdump_command
from groundstation.models import Decoder, Observation, Radio, Satellite

SATELLITE = Satellite("METEOR-M2 4", 59051, 137_100_000, "LRPT")
OBSERVATION = Observation(
    "id", SATELLITE, datetime.now(UTC), 10, 137_100_000, 1_024_000, Path("capture")
)


def test_rtl_command_has_bounded_sample_count():
    radio = Radio("rtl_sdr", "0", 1_024_000, 38.6, 1, False)
    command = rtl_sdr_command(radio, OBSERVATION)
    assert command[command.index("-n") + 1] == "10240000"
    assert command[-1].endswith("baseband.cu8")


def test_satdump_command_selects_meteor_variant():
    decoder = Decoder("satdump", "satdump", "meteor_m2-x_lrpt", "baseband")
    command = satdump_command(decoder, OBSERVATION)
    assert command[:3] == ["satdump", "pipeline", "meteor_m2-x_lrpt"]
    assert command[-1] == "M2-4"
    assert "--baseband_format" in command

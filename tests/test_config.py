from pathlib import Path

from groundstation.config import load_config


def test_example_configuration_loads():
    config = load_config(Path("config/station.example.toml"))
    assert config.station.name == "My Ground Station"
    assert {sat.norad_id for sat in config.satellites} == {57166, 59051}
    assert config.storage_root.name == "observations"

from pathlib import Path

from groundstation.executables import resolve_executable


def test_resolves_explicit_executable_path(tmp_path: Path):
    executable = tmp_path / "custom-satdump"
    executable.touch()
    assert resolve_executable(str(executable)) == str(executable)


def test_missing_executable_returns_none():
    assert resolve_executable("definitely-not-a-real-groundstation-tool") is None

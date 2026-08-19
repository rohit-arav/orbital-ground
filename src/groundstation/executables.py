from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

MACOS_CANDIDATES: dict[str, tuple[str, ...]] = {
    "satdump": (
        "/Applications/SatDump.app/Contents/MacOS/satdump",
        "/opt/homebrew/bin/satdump",
        "/usr/local/bin/satdump",
    ),
    "rtl_sdr": (
        "/opt/homebrew/bin/rtl_sdr",
        "/usr/local/bin/rtl_sdr",
    ),
}


def resolve_executable(command: str) -> str | None:
    """Resolve a configured command, including common macOS install locations."""
    expanded = Path(os.path.expandvars(command)).expanduser()
    if (expanded.is_absolute() or expanded.parent != Path(".")) and expanded.is_file():
        return str(expanded)
    found = shutil.which(command)
    if found:
        return found
    if sys.platform == "darwin":
        for candidate in MACOS_CANDIDATES.get(Path(command).name, ()):
            path = Path(candidate)
            if path.is_file() and os.access(path, os.X_OK):
                return str(path)
    return None

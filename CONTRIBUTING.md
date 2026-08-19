# Contributing

Contributions that make the station safer, more reproducible, or easier to learn from are welcome.

## Development setup

Create a Python 3.11+ virtual environment and install the editable development package:

```text
python -m pip install -e ".[dev]"
```

Before opening a pull request, run:

```text
python -m ruff check .
python -m pytest
```

Tests must not require connected radio hardware, a network connection, or precise station
coordinates. Keep hardware and external-program behavior behind adapters so it can be simulated.

## Privacy and observation data

Never commit precise residential coordinates, credentials, raw IQ recordings, generated satellite
products, or locally downloaded orbital elements. Use `config/station.example.toml` for documented
examples and verify ignored files with `git status --ignored` before publishing.

## Scope

This is a receive-focused educational project. Features involving transmission must be clearly
separated, disabled by default, and document the need to comply with local radio regulations.


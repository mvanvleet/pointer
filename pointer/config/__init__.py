try:
    import tomllib  # Python >= 3.11
except ModuleNotFoundError:
    import tomli as tomllib  # backwards-compatible for Python < 3.11

from pathlib import PurePath

settingsfile = PurePath(__file__).parent / "default.toml"
with open(settingsfile, mode="rb") as f:
    settings = tomllib.load(f)

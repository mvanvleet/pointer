"""Parameter Optimization for INTERmolecular force fields fit to quantum-mechanical data."""

# Import sub-packages
from . import quantum
from ._version import __version__

# Read in configuration settings
from .config import settings


# Make sure modules have access to the data files directory, since these are
# used for both testing and examples
from pathlib import Path

DATADIR = Path(__file__).parent / "data"

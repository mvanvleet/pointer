"""Parameter Optimization for INTERmolecular force fields fit to quantum-mechanical data."""

from . import quantum

from ._version import __version__

# Make sure modules have access to the data files directory
from pathlib import PurePath
DATADIR = PurePath(__file__).parent / 'data'

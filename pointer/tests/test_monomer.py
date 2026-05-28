"""
Unit and regression test for the ionization energy module.
"""

import sys
from pathlib import Path

import pytest

from pointer import Monomer
from .. import DATADIR

TESTDIR = Path(__file__).parent / "data"

def test_blank():
    """It should be OK to have a blank monomer object"""
    foo = Monomer()

def test_h2o():
    """Test parsing of a molecule with one conformer"""

    xyzfile = Path(DATADIR,'molecules/','h2o.xyz')
    h2o = Monomer(xyzfile)

    assert h2o.natoms == 3
    assert h2o.elements == ['H','O','H']
    assert h2o.atomtypes == ['H','O','H']
    assert h2o.nconformers == 1
    assert h2o.xyz.shape == (1,3,3)

def test_mthp():
    """Test parsing of a molecule with multiple conformers"""

    xyzfile = Path(DATADIR,'molecules/','2mthpax.xyz')
    mthp = Monomer(xyzfile)

    assert mthp.natoms == 20
    assert mthp.nconformers == 4
    assert mthp.xyz.shape == (4,20,3)

def test_badxyz():
    """Make sure .xyz files not following correct syntax have appropriate
    exceptions."""

    xyzfile = Path(TESTDIR  / 'bad.xyz')
    with pytest.raises(ValueError):
        bad = Monomer(xyzfile)

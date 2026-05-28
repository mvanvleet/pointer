"""
Unit and regression test for the ionization energy module.
"""

import sys
from pathlib import Path

import pytest

from pointer.quantum import molpro, acshift
from ..molecules import Monomer
from .. import DATADIR

def test_bad_input():
    """Feeding in an argument that isn't a monomer type should raise an error"""
    with pytest.raises(AttributeError):
        acshift.get_acshift('mthp')

def test_input():
    xyzfile = Path(DATADIR,'molecules/','2mthpax.xyz')
    mthp = Monomer(xyzfile,charge=0)

    acshift.get_acshift(mthp)

def test_molpro_parse_ip_output():
    """Test parsing of Molpro IP Calculation Files"""

    ofile = Path(DATADIR,'quantum/','h2o_ip.out')
    ip, homo = molpro.parse_ionization(ofile)
    expected_ip, expected_homo = 0.46602931, -0.333967

    assert pytest.approx(ip) == expected_ip
    assert pytest.approx(homo) == expected_homo

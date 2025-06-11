"""
Unit and regression test for the ionization energy module.
"""

import sys

import pytest

from pointer.quantum import molpro


def test_molpro_process_ip():
    """Test parsing of Molpro IP Calculation Files"""

    ip, homo = molpro.process_ionization("data/quantum/h2o_ip.out")
    expected_ip, expected_homo = 0.46602931, -0.333967

    assert pytest.approx(ip) == expected_ip
    assert pytest.approx(homo) == expected_homo

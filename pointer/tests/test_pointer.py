"""
Unit and regression test for the pointer package.
"""

import sys

import pytest

import pointer


def test_pointer_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "pointer" in sys.modules

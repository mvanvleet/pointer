"""
Unit and regression test for the pointer package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import pointer


def test_pointer_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "pointer" in sys.modules

"""Shared test fixtures and configuration."""

from __future__ import annotations

import pytest
import pyvista as pv


@pytest.fixture(autouse=True)
def _ensure_pyvista_offscreen():
    """Ensure PyVista runs in off-screen mode for tests."""
    pv.OFF_SCREEN = True
    yield
    pv.OFF_SCREEN = False

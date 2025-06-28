"""Shared test fixtures and configuration."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _ensure_pyvista_offscreen():
    """Ensure PyVista runs in off-screen mode for tests."""
    import pyvista as pv

    pv.OFF_SCREEN = True
    yield
    pv.OFF_SCREEN = False

"""
Unit Tests for Coordinate Mapper
=================================
Verifies mathematical correctness, boundary behavior, inverse mapping,
and multi-map scaling against the official LILA BLACK dataset specification.
"""

import pytest
import numpy as np
import pandas as pd
from src.coordinate_mapper import (
    world_to_uv,
    uv_to_pixel,
    world_to_pixel,
    pixel_to_world,
    is_within_bounds,
    add_map_coordinates,
    get_map_config,
    MAP_CONFIGS
)


def test_readme_ambrose_valley_example():
    """Verify exact match with the README worked example."""
    # Example from README:
    # World position: x=-301.45, z=-355.55
    # AmbroseValley: scale=900, origin=(-370, -473)
    # Expected: u = 0.0762, v = 0.1305, pixel_x = 78, pixel_y = 890
    u, v = world_to_uv(-301.45, -355.55, "AmbroseValley")
    px, py = uv_to_pixel(u, v, width=1024, height=1024)

    assert round(u, 4) == 0.0762
    assert round(v, 4) == 0.1305
    assert round(px) == 78
    assert round(py) == 890


def test_grand_rift_boundaries():
    """Verify GrandRift origin, maximum, and center coordinates."""
    # Origin (-290, -290) -> (u=0, v=0) -> pixel (0, 1024)
    u0, v0 = world_to_uv(-290.0, -290.0, "GrandRift")
    px0, py0 = uv_to_pixel(u0, v0, 1024, 1024)
    assert u0 == 0.0
    assert v0 == 0.0
    assert px0 == 0.0
    assert py0 == 1024.0

    # Max corner: (-290 + 581 = 291, -290 + 581 = 291) -> (u=1, v=1) -> pixel (1024, 0)
    u1, v1 = world_to_uv(291.0, 291.0, "GrandRift")
    px1, py1 = uv_to_pixel(u1, v1, 1024, 1024)
    assert u1 == 1.0
    assert v1 == 1.0
    assert px1 == 1024.0
    assert py1 == 0.0

    # Center: (-290 + 581/2 = 0.5, 0.5)
    uc, vc = world_to_uv(0.5, 0.5, "GrandRift")
    assert round(uc, 4) == 0.5
    assert round(vc, 4) == 0.5


def test_lockdown_center_and_bounds():
    """Verify Lockdown origin and center coordinates."""
    # Origin (-500, -500), scale=1000
    u0, v0 = world_to_uv(-500.0, -500.0, "Lockdown")
    assert u0 == 0.0
    assert v0 == 0.0

    # Center is (0.0, 0.0) -> (u=0.5, v=0.5) -> pixel (512, 512)
    uc, vc = world_to_uv(0.0, 0.0, "Lockdown")
    pxc, pyc = uv_to_pixel(uc, vc, 1024, 1024)
    assert uc == 0.5
    assert vc == 0.5
    assert pxc == 512.0
    assert pyc == 512.0


def test_inverse_mapping_roundtrip():
    """Test round-trip fidelity between world and pixel coordinates."""
    test_points = [
        ("AmbroseValley", -100.0, 200.0),
        ("AmbroseValley", 50.0, -50.0),
        ("GrandRift", 10.0, -20.0),
        ("Lockdown", 150.0, -150.0),
    ]

    for map_id, wx, wz in test_points:
        px, py = world_to_pixel(wx, wz, map_id, 1024, 1024)
        rx, rz = pixel_to_world(px, py, map_id, 1024, 1024)
        assert abs(rx - wx) < 1e-4
        assert abs(rz - wz) < 1e-4


def test_add_map_coordinates_dataframe():
    """Test vectorized coordinate addition on a pandas DataFrame."""
    df = pd.DataFrame({
        'map_id': ['AmbroseValley', 'GrandRift', 'Lockdown'],
        'x': [-301.45, -290.0, 0.0],
        'z': [-355.55, -290.0, 0.0]
    })
    result = add_map_coordinates(df, width=1024, height=1024)

    assert 'u' in result.columns
    assert 'v' in result.columns
    assert 'pixel_x' in result.columns
    assert 'pixel_y' in result.columns

    # AmbroseValley row
    assert round(result.loc[0, 'pixel_x']) == 78
    assert round(result.loc[0, 'pixel_y']) == 890

    # GrandRift row
    assert result.loc[1, 'pixel_x'] == 0.0
    assert result.loc[1, 'pixel_y'] == 1024.0

    # Lockdown row
    assert result.loc[2, 'pixel_x'] == 512.0
    assert result.loc[2, 'pixel_y'] == 512.0


def test_boundary_checks():
    """Test is_within_bounds logic."""
    assert is_within_bounds(0.0, 0.0, "AmbroseValley")
    assert is_within_bounds(0.0, 0.0, "GrandRift")
    assert is_within_bounds(0.0, 0.0, "Lockdown")

    # Far out-of-bounds coordinates
    assert not is_within_bounds(5000.0, 5000.0, "AmbroseValley")
    assert not is_within_bounds(-2000.0, -2000.0, "Lockdown")


def test_invalid_map_raises_error():
    """Verify that unknown map names raise a clear ValueError."""
    with pytest.raises(ValueError, match="Unknown map_id"):
        world_to_uv(0, 0, "NonExistentMap")

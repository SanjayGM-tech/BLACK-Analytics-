"""
Coordinate Mapper for LILA BLACK Game Telemetry
================================================
Handles conversion between 3D in-game world coordinates and 2D minimap coordinates.

Coordinate Conventions:
- Game World:
    x: Horizontal (East / West)
    y: Vertical elevation (Height above sea level, NOT used for 2D minimap)
    z: Depth / North-South (Corresponds to vertical map axis)
- Minimap Space:
    u: Normalized horizontal coordinate in [0, 1] (0 = left, 1 = right)
    v: Normalized vertical coordinate in [0, 1] (0 = bottom, 1 = top)
    pixel_x: Canvas pixel column in [0, width] (0 = left, width = right)
    pixel_y: Canvas pixel row in [0, height] (0 = top, height = bottom, inverted)

Formulas:
    u = (x - origin_x) / scale
    v = (z - origin_z) / scale
    pixel_x = u * width
    pixel_y = (1.0 - v) * height
"""

from typing import Dict, Tuple, Union, Optional
import numpy as np
import pandas as pd


MAP_CONFIGS: Dict[str, Dict[str, Union[float, str]]] = {
    "AmbroseValley": {
        "scale": 900.0,
        "origin_x": -370.0,
        "origin_z": -473.0,
        "minimap_file": "AmbroseValley_Minimap.png",
        "name": "Ambrose Valley"
    },
    "GrandRift": {
        "scale": 581.0,
        "origin_x": -290.0,
        "origin_z": -290.0,
        "minimap_file": "GrandRift_Minimap.png",
        "name": "Grand Rift"
    },
    "Lockdown": {
        "scale": 1000.0,
        "origin_x": -500.0,
        "origin_z": -500.0,
        "minimap_file": "Lockdown_Minimap.jpg",
        "name": "Lockdown"
    }
}


def get_map_config(map_id: str) -> Dict[str, Union[float, str]]:
    """Retrieve configuration parameters for a given map identifier."""
    if map_id not in MAP_CONFIGS:
        raise ValueError(
            f"Unknown map_id '{map_id}'. Supported maps: {list(MAP_CONFIGS.keys())}"
        )
    return MAP_CONFIGS[map_id]


def world_to_uv(
    x: Union[float, np.ndarray, pd.Series],
    z: Union[float, np.ndarray, pd.Series],
    map_id: str
) -> Tuple[Union[float, np.ndarray, pd.Series], Union[float, np.ndarray, pd.Series]]:
    """
    Convert world coordinates (x, z) to normalized UV coordinates [0.0, 1.0].
    
    Args:
        x: World X coordinate (East-West)
        z: World Z coordinate (North-South)
        map_id: Map identifier ('AmbroseValley', 'GrandRift', 'Lockdown')
        
    Returns:
        (u, v): Normalized map coordinates where u in [0, 1] and v in [0, 1].
    """
    config = get_map_config(map_id)
    origin_x = config["origin_x"]
    origin_z = config["origin_z"]
    scale = config["scale"]

    u = (x - origin_x) / scale
    v = (z - origin_z) / scale
    return u, v


def uv_to_pixel(
    u: Union[float, np.ndarray, pd.Series],
    v: Union[float, np.ndarray, pd.Series],
    width: float = 1024.0,
    height: float = 1024.0
) -> Tuple[Union[float, np.ndarray, pd.Series], Union[float, np.ndarray, pd.Series]]:
    """
    Convert normalized UV coordinates to canvas pixel coordinates.
    Notice that the image origin is at the top-left, so pixel_y = (1.0 - v) * height.
    """
    pixel_x = u * width
    pixel_y = (1.0 - v) * height
    return pixel_x, pixel_y


def world_to_pixel(
    x: Union[float, np.ndarray, pd.Series],
    z: Union[float, np.ndarray, pd.Series],
    map_id: str,
    width: float = 1024.0,
    height: float = 1024.0
) -> Tuple[Union[float, np.ndarray, pd.Series], Union[float, np.ndarray, pd.Series]]:
    """Directly convert world (x, z) to canvas pixel coordinates."""
    u, v = world_to_uv(x, z, map_id)
    return uv_to_pixel(u, v, width=width, height=height)


def pixel_to_world(
    pixel_x: float,
    pixel_y: float,
    map_id: str,
    width: float = 1024.0,
    height: float = 1024.0
) -> Tuple[float, float]:
    """Inverse transformation: canvas pixel coordinates to in-game world (x, z)."""
    config = get_map_config(map_id)
    origin_x = config["origin_x"]
    origin_z = config["origin_z"]
    scale = config["scale"]

    u = pixel_x / width
    v = 1.0 - (pixel_y / height)

    x = u * scale + origin_x
    z = v * scale + origin_z
    return x, z


def is_within_bounds(
    x: float,
    z: float,
    map_id: str,
    margin: float = 0.05
) -> bool:
    """Check if a world coordinate falls within normalized map bounds with optional margin."""
    u, v = world_to_uv(x, z, map_id)
    return (-margin <= u <= 1.0 + margin) and (-margin <= v <= 1.0 + margin)


def add_map_coordinates(
    df: pd.DataFrame,
    width: float = 1024.0,
    height: float = 1024.0
) -> pd.DataFrame:
    """
    Vectorized addition of normalized and pixel coordinates to a telemetry DataFrame.
    Operates per map_id present in the DataFrame.
    """
    if df.empty or 'x' not in df.columns or 'z' not in df.columns:
        return df

    df = df.copy()
    df['u'] = np.nan
    df['v'] = np.nan
    df['pixel_x'] = np.nan
    df['pixel_y'] = np.nan

    for map_id in df['map_id'].unique():
        if map_id in MAP_CONFIGS:
            mask = df['map_id'] == map_id
            u, v = world_to_uv(df.loc[mask, 'x'], df.loc[mask, 'z'], map_id)
            px, py = uv_to_pixel(u, v, width=width, height=height)
            df.loc[mask, 'u'] = u
            df.loc[mask, 'v'] = v
            df.loc[mask, 'pixel_x'] = px
            df.loc[mask, 'pixel_y'] = py

    return df

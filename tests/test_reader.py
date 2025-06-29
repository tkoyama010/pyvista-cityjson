"""Tests for CityJSONReader."""

from __future__ import annotations

import json

import pytest

from pyvista_cityjson import read_cityjson
from pyvista_cityjson.reader import CityJSONReader


@pytest.fixture
def sample_cityjson_data():
    """Create sample CityJSON data for testing."""
    return {
        "type": "CityJSON",
        "version": "1.1",
        "vertices": [
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1],
        ],
        "CityObjects": {
            "building1": {
                "type": "Building",
                "geometry": [
                    {
                        "type": "Solid",
                        "boundaries": [
                            [
                                [[0, 1, 2, 3]],  # bottom
                                [[4, 5, 6, 7]],  # top
                                [[0, 1, 5, 4]],  # front
                                [[2, 3, 7, 6]],  # back
                                [[0, 3, 7, 4]],  # left
                                [[1, 2, 6, 5]],  # right
                            ]
                        ],
                    }
                ],
            }
        },
    }


@pytest.fixture
def sample_cityjson_file(tmp_path, sample_cityjson_data):
    """Create a temporary CityJSON file for testing."""
    file_path = tmp_path / "test.city.json"
    with file_path.open("w") as f:
        json.dump(sample_cityjson_data, f)
    return file_path


def test_reader_initialization(sample_cityjson_file):
    """Test CityJSONReader initialization."""
    reader = CityJSONReader(sample_cityjson_file)
    assert reader.filename == sample_cityjson_file
    assert reader.data is not None
    assert reader.mesh is not None


def test_invalid_file_format(tmp_path):
    """Test that invalid CityJSON files raise ValueError."""
    invalid_file = tmp_path / "invalid.json"
    with invalid_file.open("w") as f:
        json.dump({"type": "NotCityJSON"}, f)

    with pytest.raises(ValueError, match="Invalid CityJSON file"):
        CityJSONReader(invalid_file)


def test_mesh_creation(sample_cityjson_file):
    """Test mesh creation from CityJSON data."""
    reader = CityJSONReader(sample_cityjson_file)
    mesh = reader.mesh

    # Check that mesh has vertices
    assert mesh.n_points == 8  # cube has 8 vertices
    assert mesh.n_cells > 0  # should have faces

    # Check cell data
    assert "object_type" in mesh.cell_data
    assert "object_id" in mesh.cell_data


def test_filter_by_type(sample_cityjson_file):
    """Test filtering mesh by object type."""
    reader = CityJSONReader(sample_cityjson_file)

    # Filter for buildings
    building_mesh = reader.filter_by_type("Building")
    assert building_mesh is not None
    assert building_mesh.n_cells > 0

    # Filter for non-existent type
    bridge_mesh = reader.filter_by_type("Bridge")
    assert bridge_mesh is None


def test_empty_cityjson(tmp_path):
    """Test handling of empty CityJSON file."""
    empty_data = {
        "type": "CityJSON",
        "version": "1.1",
        "vertices": [],
        "CityObjects": {},
    }
    empty_file = tmp_path / "empty.city.json"
    with empty_file.open("w") as f:
        json.dump(empty_data, f)

    reader = CityJSONReader(empty_file)
    assert reader.mesh.n_points == 0
    assert reader.mesh.n_cells == 0


def test_multisurface_geometry(tmp_path):
    """Test handling of MultiSurface geometry."""
    multisurface_data = {
        "type": "CityJSON",
        "version": "1.1",
        "vertices": [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]],
        "CityObjects": {
            "surface1": {
                "type": "Building",
                "geometry": [{"type": "MultiSurface", "boundaries": [[[0, 1, 2, 3]]]}],
            }
        },
    }
    file_path = tmp_path / "multisurface.city.json"
    with file_path.open("w") as f:
        json.dump(multisurface_data, f)

    reader = CityJSONReader(file_path)
    assert reader.mesh.n_cells == 1


def test_color_by_surface(sample_cityjson_file):
    """Test color_by_surface method."""
    reader = CityJSONReader(sample_cityjson_file)
    colored_mesh = reader.color_by_surface()
    assert colored_mesh is not None


def test_read_cityjson_function(sample_cityjson_file):
    """Test the read_cityjson convenience function."""
    mesh = read_cityjson(sample_cityjson_file)

    assert mesh is not None
    assert mesh.n_points == 8  # cube has 8 vertices
    assert mesh.n_cells > 0  # should have faces

    # Check cell data
    assert "object_type" in mesh.cell_data
    assert "object_id" in mesh.cell_data


def test_read_cityjson_with_pathlib_path(sample_cityjson_file):
    """Test read_cityjson with pathlib.Path input."""
    from pathlib import Path

    mesh = read_cityjson(Path(sample_cityjson_file))
    assert mesh is not None
    assert mesh.n_points == 8


def test_read_cityjson_file_not_found():
    """Test read_cityjson with non-existent file."""
    with pytest.raises(FileNotFoundError, match="File not found"):
        read_cityjson("non_existent_file.json")


def test_read_cityjson_invalid_json(tmp_path):
    """Test read_cityjson with invalid JSON file."""
    invalid_json_file = tmp_path / "invalid.json"
    with invalid_json_file.open("w") as f:
        f.write("This is not valid JSON{")

    with pytest.raises(ValueError, match="Invalid JSON file"):
        read_cityjson(invalid_json_file)


def test_read_cityjson_invalid_cityjson(tmp_path):
    """Test read_cityjson with valid JSON but invalid CityJSON."""
    invalid_cityjson = tmp_path / "not_cityjson.json"
    with invalid_cityjson.open("w") as f:
        json.dump({"type": "NotCityJSON", "data": "something"}, f)

    with pytest.raises(ValueError, match="Invalid CityJSON file"):
        read_cityjson(invalid_cityjson)

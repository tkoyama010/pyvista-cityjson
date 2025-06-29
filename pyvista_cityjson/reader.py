"""CityJSON Reader for PyVista.

Loads CityJSON files and converts them to PyVista meshes for visualization.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pyvista as pv

try:
    import pyvista as pv
except ImportError:
    pv = None


class CityJSONReader:
    """Reader for CityJSON files that converts geometries to PyVista meshes.

    Parameters
    ----------
    filename : str
        Path to the CityJSON file

    """

    def __init__(self, filename: str | Path) -> None:
        """Initialize the CityJSON reader.

        Parameters
        ----------
        filename : str | Path
            Path to the CityJSON file to read.

        Raises
        ------
        ImportError
            If PyVista is not installed.
        ValueError
            If the file is not a valid CityJSON file.

        """
        if pv is None:
            msg = "PyVista is required. Install with: pip install pyvista"
            raise ImportError(msg)

        self.filename = filename
        self._data = None
        self._mesh = None
        self._load_file()

    def _load_file(self) -> None:
        """Load and parse the CityJSON file."""
        try:
            with Path(self.filename).open() as f:
                self._data = json.load(f)
        except FileNotFoundError as e:
            msg = f"File not found: {self.filename}"
            raise FileNotFoundError(msg) from e
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON file: {self.filename}"
            raise ValueError(msg) from e

        # Validate CityJSON format
        if self._data.get("type") != "CityJSON":
            msg = f"Invalid CityJSON file: {self.filename}"
            raise ValueError(msg)

        self._create_mesh()

    def _create_mesh(self) -> None:
        """Convert CityJSON geometries to PyVista mesh."""
        vertices = np.array(self._data.get("vertices", []))
        if len(vertices) == 0:
            self._mesh = pv.PolyData()
            return

        # Collect all faces from all city objects
        all_faces = []
        cell_data = {"object_type": [], "object_id": []}

        city_objects = self._data.get("CityObjects", {})

        for obj_id, obj_data in city_objects.items():
            obj_type = obj_data.get("type", "Unknown")
            geometries = obj_data.get("geometry", [])

            for geom in geometries:
                faces = self._extract_faces_from_geometry(geom)
                for face in faces:
                    all_faces.append([len(face), *face])
                    cell_data["object_type"].append(obj_type)
                    cell_data["object_id"].append(obj_id)

        if len(all_faces) == 0:
            self._mesh = pv.PolyData()
            return

        # Create PyVista mesh
        faces = np.hstack(all_faces)
        self._mesh = pv.PolyData(vertices, faces)

        # Add cell data
        for key, values in cell_data.items():
            if len(values) > 0:
                self._mesh.cell_data[key] = values

    def _extract_faces_from_geometry(self, geometry: dict) -> list[list[int]]:
        """Extract face indices from CityJSON geometry."""
        geom_type = geometry.get("type", "")
        boundaries = geometry.get("boundaries", [])

        if geom_type == "Solid":
            return self._extract_solid_faces(boundaries)
        if geom_type in {"MultiSurface", "CompositeSurface"}:
            return self._extract_surface_faces(boundaries)
        return []

    def _extract_solid_faces(self, boundaries: list) -> list[list[int]]:
        """Extract faces from Solid geometry."""
        faces = []
        for shell in boundaries:
            for face_def in shell:
                if isinstance(face_def, list) and len(face_def) > 0:
                    face = face_def[0] if isinstance(face_def[0], list) else face_def
                    if self._is_valid_face(face):
                        faces.append(face)
        return faces

    def _extract_surface_faces(self, boundaries: list) -> list[list[int]]:
        """Extract faces from MultiSurface/CompositeSurface geometry."""
        faces = []
        for face_def in boundaries:
            face = (
                face_def[0]
                if isinstance(face_def, list) and isinstance(face_def[0], list)
                else face_def
            )
            if self._is_valid_face(face):
                faces.append(face)
        return faces

    def _is_valid_face(self, face: list) -> bool:
        """Check if a face has the minimum required vertices."""
        min_vertices = 3
        return len(face) >= min_vertices

    @property
    def mesh(self) -> pv.PolyData:
        """Get the PyVista mesh representation."""
        return self._mesh

    @property
    def data(self) -> dict:
        """Get the raw CityJSON data."""
        return self._data

    def filter_by_type(self, object_type: str) -> pv.PolyData | None:
        """Filter mesh by city object type.

        Parameters
        ----------
        object_type : str
            Type of city object to filter (e.g., 'Building', 'Bridge')

        Returns
        -------
        pyvista.PolyData or None
            Filtered mesh containing only objects of the specified type

        """
        if self._mesh is None or "object_type" not in self._mesh.cell_data:
            return None

        # Find cells that match the object type
        cell_mask = np.array(self._mesh.cell_data["object_type"]) == object_type

        if not np.any(cell_mask):
            return None

        # Extract matching cells
        cell_indices = np.where(cell_mask)[0]
        return self._mesh.extract_cells(cell_indices)

    def color_by_surface(self) -> pv.PolyData | None:
        """Color mesh by semantic surface types.

        Returns
        -------
        pyvista.PolyData or None
            Mesh with surface-based coloring

        """
        # This is a simplified implementation
        # In a real implementation, you would parse semantic surface information
        if self._mesh is None:
            return None

        # For now, just color by object type
        if "object_type" in self._mesh.cell_data:
            return self._mesh.copy()

        return None


def read_cityjson(filename: str | Path) -> pv.PolyData:
    """Read a CityJSON file and return a PyVista mesh.

    Parameters
    ----------
    filename : str | Path
        Path to the CityJSON file to read.

    Returns
    -------
    pyvista.PolyData
        PyVista mesh representation of the CityJSON data.

    Raises
    ------
    ImportError
        If PyVista is not installed.
    ValueError
        If the file is not a valid CityJSON file.
    FileNotFoundError
        If the specified file does not exist.

    Examples
    --------
    >>> import pyvista_cityjson
    >>> mesh = pyvista_cityjson.read_cityjson("city.json")
    >>> mesh.plot()

    """
    reader = CityJSONReader(filename)
    return reader.mesh

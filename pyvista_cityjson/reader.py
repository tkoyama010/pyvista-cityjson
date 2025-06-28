"""
CityJSON Reader for PyVista

Loads CityJSON files and converts them to PyVista meshes for visualization.
"""

import json
import numpy as np
try:
    import pyvista as pv
except ImportError:
    pv = None


class CityJSONReader:
    """
    Reader for CityJSON files that converts geometries to PyVista meshes.
    
    Parameters
    ----------
    filename : str
        Path to the CityJSON file
    """
    
    def __init__(self, filename):
        if pv is None:
            raise ImportError("PyVista is required. Install with: pip install pyvista")
        
        self.filename = filename
        self._data = None
        self._mesh = None
        self._load_file()
    
    def _load_file(self):
        """Load and parse the CityJSON file."""
        with open(self.filename, 'r') as f:
            self._data = json.load(f)
        
        # Validate CityJSON format
        if self._data.get('type') != 'CityJSON':
            raise ValueError(f"Invalid CityJSON file: {self.filename}")
        
        self._create_mesh()
    
    def _create_mesh(self):
        """Convert CityJSON geometries to PyVista mesh."""
        vertices = np.array(self._data.get('vertices', []))
        if len(vertices) == 0:
            self._mesh = pv.PolyData()
            return
        
        # Collect all faces from all city objects
        all_faces = []
        cell_data = {'object_type': [], 'object_id': []}
        
        city_objects = self._data.get('CityObjects', {})
        
        for obj_id, obj_data in city_objects.items():
            obj_type = obj_data.get('type', 'Unknown')
            geometries = obj_data.get('geometry', [])
            
            for geom in geometries:
                faces = self._extract_faces_from_geometry(geom)
                for face in faces:
                    all_faces.append([len(face)] + face)
                    cell_data['object_type'].append(obj_type)
                    cell_data['object_id'].append(obj_id)
        
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
    
    def _extract_faces_from_geometry(self, geometry):
        """Extract face indices from CityJSON geometry."""
        faces = []
        geom_type = geometry.get('type', '')
        boundaries = geometry.get('boundaries', [])
        
        if geom_type == 'Solid':
            # Solid geometry - extract all boundary faces
            for shell in boundaries:
                for face_def in shell:
                    # Handle nested face definitions
                    if isinstance(face_def, list) and len(face_def) > 0:
                        # Get the outer ring (first element)
                        face = face_def[0] if isinstance(face_def[0], list) else face_def
                        if len(face) >= 3:  # Valid face needs at least 3 vertices
                            faces.append(face)
        
        elif geom_type == 'MultiSurface':
            # MultiSurface - each boundary is a face
            for face_def in boundaries:
                face = face_def[0] if isinstance(face_def, list) and isinstance(face_def[0], list) else face_def
                if len(face) >= 3:
                    faces.append(face)
        
        elif geom_type == 'CompositeSurface':
            # CompositeSurface - similar to MultiSurface
            for face_def in boundaries:
                face = face_def[0] if isinstance(face_def, list) and isinstance(face_def[0], list) else face_def
                if len(face) >= 3:
                    faces.append(face)
        
        return faces
    
    @property
    def mesh(self):
        """Get the PyVista mesh representation."""
        return self._mesh
    
    @property 
    def data(self):
        """Get the raw CityJSON data."""
        return self._data
    
    def filter_by_type(self, object_type):
        """
        Filter mesh by city object type.
        
        Parameters
        ----------
        object_type : str
            Type of city object to filter (e.g., 'Building', 'Bridge')
        
        Returns
        -------
        pyvista.PolyData or None
            Filtered mesh containing only objects of the specified type
        """
        if self._mesh is None or 'object_type' not in self._mesh.cell_data:
            return None
        
        # Find cells that match the object type
        cell_mask = np.array(self._mesh.cell_data['object_type']) == object_type
        
        if not np.any(cell_mask):
            return None
        
        # Extract matching cells
        cell_indices = np.where(cell_mask)[0]
        return self._mesh.extract_cells(cell_indices)
    
    def color_by_surface(self):
        """
        Color mesh by semantic surface types.
        
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
        if 'object_type' in self._mesh.cell_data:
            return self._mesh.copy()
        
        return None
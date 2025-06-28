#!/usr/bin/env python3
"""
Example: Visualizing Two Cubes from CityJSON

This example demonstrates how to load and visualize a CityJSON file
containing two cube geometries using pyvista-cityjson.
"""

import pyvista as pv
from pyvista_cityjson import CityJSONReader


def main():
    # Load the twocube.city.json file
    reader = CityJSONReader("twocube.city.json")
    
    # Get the complete mesh
    mesh = reader.mesh
    
    # Create a plotter for visualization
    plotter = pv.Plotter(window_size=(1024, 768))
    plotter.add_mesh(mesh, show_edges=True, color="lightblue")
    plotter.add_title("Two Cubes CityJSON Visualization")
    
    # Add lighting and camera settings for better visualization
    plotter.add_light(pv.Light(position=(10, 10, 10)))
    plotter.camera_position = 'isometric'
    
    # Show the interactive plot
    plotter.show()
    
    # Example: Filter buildings only
    buildings = reader.filter_by_type("Building")
    if buildings is not None:
        print(f"Found {buildings.n_cells} building cells")
        
        # Create a separate plot for buildings only
        building_plotter = pv.Plotter(window_size=(1024, 768))
        building_plotter.add_mesh(buildings, show_edges=True, color="orange")
        building_plotter.add_title("Buildings Only")
        building_plotter.camera_position = 'isometric'
        building_plotter.show()
    
    # Example: Color by semantic surfaces
    try:
        colored_mesh = reader.color_by_surface()
        if colored_mesh is not None:
            surface_plotter = pv.Plotter(window_size=(1024, 768))
            surface_plotter.add_mesh(colored_mesh, show_edges=True)
            surface_plotter.add_title("Colored by Semantic Surfaces")
            surface_plotter.camera_position = 'isometric'
            surface_plotter.show()
    except Exception as e:
        print(f"Could not color by surfaces: {e}")


if __name__ == "__main__":
    main()
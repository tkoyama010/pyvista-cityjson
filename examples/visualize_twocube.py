#!/usr/bin/env python3
"""Example: Visualizing Two Cubes from CityJSON.

This example demonstrates how to load and visualize a CityJSON file
containing two cube geometries using pyvista-cityjson.
"""

import os
import sys
from pathlib import Path

import pyvista as pv

from pyvista_cityjson import CityJSONReader


def main() -> None:
    """Run the main visualization example."""
    # Change to examples directory if running from parent directory
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    # Load the twocube.city.json file
    cityjson_file = "twocube.city.json"
    cityjson_path = Path(cityjson_file)
    if not cityjson_path.exists():
        msg = f"Error: {cityjson_file} not found in {Path.cwd()}"
        sys.stderr.write(msg + "\n")
        sys.stderr.write(
            "Make sure to run this script from the examples directory "
            "or ensure the file exists.\n"
        )
        sys.exit(1)

    reader = CityJSONReader(cityjson_file)

    # Get the complete mesh
    mesh = reader.mesh

    # Create a plotter for visualization
    plotter = pv.Plotter(window_size=(1024, 768))
    plotter.add_mesh(mesh, show_edges=True, color="lightblue")
    plotter.add_title("Two Cubes CityJSON Visualization")

    # Add lighting and camera settings for better visualization
    plotter.add_light(pv.Light(position=(10, 10, 10)))
    plotter.camera_position = "iso"

    # Export to HTML
    output_file = "twocube_visualization.html"
    plotter.export_html(output_file)
    output_path = Path(output_file).resolve()
    sys.stdout.write(f"Main visualization exported to: {output_path}\n")

    # Example: Filter buildings only
    buildings = reader.filter_by_type("Building")
    if buildings is not None:
        sys.stdout.write(f"Found {buildings.n_cells} building cells\n")

        # Create a separate plot for buildings only
        building_plotter = pv.Plotter(window_size=(1024, 768))
        building_plotter.add_mesh(buildings, show_edges=True, color="orange")
        building_plotter.add_title("Buildings Only")
        building_plotter.camera_position = "iso"
        buildings_file = "buildings_only.html"
        building_plotter.export_html(buildings_file)
        buildings_path = Path(buildings_file).resolve()
        sys.stdout.write(f"Buildings visualization exported to: {buildings_path}\n")

    # Example: Color by semantic surfaces
    try:
        colored_mesh = reader.color_by_surface()
        if colored_mesh is not None:
            surface_plotter = pv.Plotter(window_size=(1024, 768))
            surface_plotter.add_mesh(colored_mesh, show_edges=True)
            surface_plotter.add_title("Colored by Semantic Surfaces")
            surface_plotter.camera_position = "iso"
            surfaces_file = "semantic_surfaces.html"
            surface_plotter.export_html(surfaces_file)
            surfaces_path = Path(surfaces_file).resolve()
            sys.stdout.write(
                f"Semantic surfaces visualization exported to: {surfaces_path}\n"
            )
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"Could not color by surfaces: {e}\n")


if __name__ == "__main__":
    main()

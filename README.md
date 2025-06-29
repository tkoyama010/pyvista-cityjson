# pyvista-cityjson

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

**Visualize CityJSON data with PyVista in Python**

[![PyPI](https://img.shields.io/pypi/v/pyvista-cityjson.svg)](https://pypi.org/project/pyvista-cityjson/)
[![License](https://img.shields.io/github/license/yourusername/pyvista-cityjson)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/pyvista-cityjson)](https://pypi.org/project/pyvista-cityjson/)

`pyvista-cityjson` is a Python library to load and visualize [CityJSON](https://www.cityjson.org/) files using [PyVista](https://github.com/pyvista/pyvista), making it easy to inspect 3D city models interactively.

## Features

- ✅ Load CityJSON files (v1.0 / v1.1) as PyVista meshes
- ✅ Visualize city objects with `pv.Plotter`
- ✅ Support for filtering by object type (e.g. Building, Bridge, etc.)
- ✅ Extract and color by semantic surfaces or LoD
- ✅ Access geometry and attributes for further processing

## Installation

```bash
pip install pyvista-cityjson
```

## Usage

```python
import pyvista as pv
from pyvista_cityjson import CityJSONReader

# Load CityJSON file
reader = CityJSONReader("path/to/your_file.city.json")

# Access PyVista mesh
mesh = reader.mesh

# Plot interactively
plotter = pv.Plotter()
plotter.add_mesh(mesh, show_edges=True)
plotter.show()
```

### Filtering by object type

```python
buildings = reader.filter_by_type("Building")
pv.Plotter().add_mesh(buildings).show()
```

### Visualize with semantic surfaces

```python
colored = reader.color_by_surface()
pv.Plotter().add_mesh(colored).show()
```

## Requirements

- Python 3.8+
- `pyvista`
- `numpy`
- `cityjson` or `cjio` (for parsing)

## Roadmap

- [ ] Support CityJSON v2.x
- [ ] Better handling of textures and materials
- [ ] Support CityJSON metadata (e.g. CRS transformation)

## Contributing

Contributions and suggestions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/tkoyama010"><img src="https://avatars.githubusercontent.com/u/7513610?v=4?s=100" width="100px;" alt="Tetsuo Koyama"/><br /><sub><b>Tetsuo Koyama</b></sub></a><br /><a href="https://github.com/tkoyama010/pyvista-cityjson/commits?author=tkoyama010" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

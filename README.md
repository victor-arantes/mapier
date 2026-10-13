# Mapier

Mapier is a terminal-first viewer for geospatial data. Open local layers,
remote files, and WFS services directly from the command line, view them in a
terminal that supports the Kitty graphics protocol, and optionally save remote
layers in another format.

> Mapier is in active release preparation. Feedback and bug reports are welcome.

## Requirements

- Linux
- A terminal with Kitty graphics protocol support, such as Kitty, Ghostty, or
  Rio

## Install

Download a Mapier `.deb` release, then install it with APT:

```bash
sudo apt install ./mapier_0.1.0-1_all.deb
```

APT installs the package and its declared dependencies.

## Quick start

Open a local geospatial file:

```bash
mapier states.gpkg
```

Open a remote layer:

```bash
mapier https://example.org/layers/regions.geojson
```

Open several sources at once:

```bash
mapier roads.gpkg boundaries.geojson
```

## Source lists

Pass a plain-text file to load every non-empty line as a source. A source can
be a local path, a URL, or a WFS service URL.

```text
./data/states.gpkg
https://example.org/layers/regions.geojson
https://example.org/geoserver/wfs
```

Run it with:

```bash
mapier sources.txt
```

## WFS layers

When Mapier receives a WFS URL, it lists the available layers and prompts you
to select the layers to view. Enter comma-separated layer numbers, or `N` to
skip them.

## Saving downloaded layers

Remote layers are loaded temporarily. After rendering, Mapier asks whether to
save them. You can select one or more layers and choose one of these formats:

- Shapefile (`.shp`)
- GeoPackage (`.gpkg`)
- GeoJSON (`.geojson`)
- GeoParquet (`.parquet`)

Saved files are written to your system Downloads directory.

## Export configuration

Use the interactive configuration menu:

```bash
mapier --config
```

The configuration is saved in:

```text
~/.config/mapier/config.toml
```

Available export-processing settings:

- **Output CRS** — preserve the source CRS or reproject before saving. Enter
  an EPSG code such as `4674` or `EPSG:4674`.
- **Repair invalid geometry** — apply `make_valid()` before writing.
- **Drop Z coordinates** — export two-dimensional geometries.

Mapier applies enabled transformations only to exported copies; the displayed
and source data are not modified.

## Build from source

Install Python dependencies for development:

```bash
python3 -m pip install -r requirements.txt
```

Build the Debian package:

```bash
./build.sh
```

The build script checks the package files, prompts before building, and places
the resulting `.deb`, `.changes`, and `.buildinfo` files in `debs/`.

## Demo

Screenshots and terminal recordings are coming soon.

## License

Mapier is licensed under the Apache License 2.0.

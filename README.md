# About Mapier

Mapier is a terminal viewer for geospatial data. Open local layers,
remote files, and WFS services directly from the command line and displays them. Designed to solve the very specific issue when you are in a SSH session or headless machine and have no way of inspecting spatial data whatsoever (or if you just wanna inspect it beforehand without opening a GIS tool or python script): 


![Mapier terminal demo](assets/demo.gif)

> Mapier is in active release preparation. Feedback and bug reports are welcome.

## General Workflow
```
mermaid
flowchart LR
    subgraph LOCAL["Local Machine"]
        direction TB
        TERM["Terminal Emulator<br/>"]
    end

    subgraph REMOTE["Remote Machine"]
        direction TB
        APP["Mapier<br/>Application Execution"]
    end

    TERM -->|"1- SSH Connection"| APP
    APP -.->|"2- Image Output via<br/>Graphics Protocol"| TERM
```

## Requirements

- Debian based Linux distro
- A terminal with [Kitty graphics protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/)
  support. Mapier has been tested with:
  - [Kitty](https://sw.kovidgoyal.net/kitty/)
  - [Ghostty](https://ghostty.org/docs/features), which supports the Kitty
    graphics protocol
  - [Rio](https://rioterm.com/), which
    supports the Kitty graphics protocol

- In case your worflow is Windows ---- SSH ----> Linux:

  - [Rio] Is the recommended terminal emulator, as it has a Windows native version (https://rioterm.com/docs/install/windows)
    - Users may experience problems with the image rendering when using Windows Rio, due to missing files needed to use the newer Windows ConPTY implementation: 
	1 - Download the Microsoft.Windows.Console.ConPTY package. 
        2 - Download the .nupkg file and extract it. A .nupkg is a ZIP archive. (https://www.nuget.org/api/v2/package/Microsoft.Windows.Console.ConPTY/1.25.260930003)
        3 - From the extracted package, copy these two files into C:\Program Files\Rio\ (or installation folder):
		- runtimes\win-x64\native\conpty.dll
		- build\native\runtimes\x64\OpenConsole.exe

## Install

<!-- latest-release:start -->
The latest release is [v0.1.4](https://github.com/victor-arantes/mapier/releases/tag/v0.1.4).

Download and install the latest package:

```bash
wget https://github.com/victor-arantes/mapier/releases/latest/download/mapier_latest_all.deb
sudo apt install ./mapier_latest_all.deb
```
<!-- latest-release:end -->

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


## License

Mapier is licensed under the Apache License 2.0.

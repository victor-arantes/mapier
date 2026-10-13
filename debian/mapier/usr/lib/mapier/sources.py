from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import pyogrio

from requester import requester, requester2, requester3


@dataclass
class Layer:
    name: str
    data: gpd.GeoDataFrame
    source: str
    download_name: str = None


def expand_source_lists(args):
    geospatial_formats = {
        f".{driver.lower()}"
        for driver in pyogrio.list_drivers()
    }
    sources = []

    for arg in args:
        path = Path(arg)

        if path.is_file() and path.suffix.lower() not in geospatial_formats:
            with path.open() as file:
                sources.extend(line.strip() for line in file if line.strip())
        else:
            sources.append(arg)

    return sources


def load_layers(sources):
    layers = []
    downloaded_layers = []
    print(f"Loading {len(sources)} source(s)...")

    for number, source in enumerate(sources, start=1):
        print(f"[{number}/{len(sources)}] {source}")
        if isinstance(source, str) and source.startswith("http"):
            remote_layers = load_remote_layers(source)
            layers.extend(remote_layers)
            downloaded_layers.extend(remote_layers)
            continue

        layers.append(
            Layer(
                name=Path(source).name,
                data=gpd.read_file(source),
                source=source,
            )
        )

    print("Layers loaded.")
    return layers, downloaded_layers


def load_remote_layers(url):
    if "wfs" in url:
        return load_wfs_layers(url)

    try:
        data, name = requester(url)
    except (TypeError, ValueError):
        data = requester(url)
        name = url.split("/")[-1]

    return [
        Layer(
            name=url.split("/")[-1],
            data=data,
            source=url,
            download_name=name,
        )
    ]


def load_wfs_layers(url):
    selected_layers = requester3(url)
    layers = []

    for layer in selected_layers:
        layers.append(
            Layer(name=layer, data=requester2(url, layer), source=layer)
        )
    return layers

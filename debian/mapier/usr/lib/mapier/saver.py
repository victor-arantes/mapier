import importlib.util
from pathlib import Path
import subprocess
import sys

import shapely

from configs import output_summary


def save_downloaded_layers(layers, config):
    if not layers:
        print("\nNo remote layers were downloaded; nothing to save.")
        return 0

    print("\nDownloaded layers:")

    for number, layer in enumerate(layers, start=1):
        if layer.source.startswith("http"):
            host = layer.source.split("//")[-1].split("/")[0]
            name = layer.source.split("/")[-1]
            print(f"  {number}. {host} — {name}")
        else:
            print(f"  {number}. {layer.name}")

    print(f"\nExport processing: {output_summary(config)}")

    download_dir = Path(
        subprocess.check_output(["xdg-user-dir", "DOWNLOAD"], text=True).strip()
    )

    while True:
        answer = input("\nSave any downloaded layers? [y/N]: ").strip().lower()

        if answer == "y":
            choices = choose_layers(layers)
            extension, geopackage_name = choose_extension()
            save_layers(layers, choices, download_dir, extension, geopackage_name, config)
            return 0

        if answer in {"", "n"}:
            print("No layers saved.")
            return 0

        print("Please enter y or n.")


def choose_layers(layers):
    while True:
        try:
            choices = [
                int(choice)
                for choice in input("Choose layers to save (numbers separated by ','): ").split(",")
            ]
        except ValueError:
            print("Please enter numbers separated by commas.")
            continue

        if all(choice in range(1, len(layers) + 1) for choice in choices):
            return choices

        print("Invalid choice. Please select from the available layers.")


def choose_extension():
    print(
        "What extension do you want to save the layers as?\n"
        " 1: .shp, 2: .gpkg, 3: .geojson, 4: .parquet"
    )

    while True:
        try:
            choice = int(input("Extension: ").strip())
        except ValueError:
            print("Please enter a valid number: 1, 2, 3, or 4.")
            continue

        extensions = {1: ".shp", 2: ".gpkg", 3: ".geojson", 4: ".parquet"}
        if choice not in extensions:
            print("Invalid extension. Please choose from 1, 2, 3, or 4.")
            continue

        if choice == 4 and not ensure_pyarrow():
            continue

        geopackage_name = None
        if choice == 2 and input(
            "Geopackage: Type 'y/Y' for one file with multiple layers: "
        ).lower() == "y":
            geopackage_name = input("Enter geopackage name: ")

        return extensions[choice], geopackage_name


def ensure_pyarrow():
    if importlib.util.find_spec("pyarrow") is not None:
        return True

    print("Parquet export requires PyArrow.")
    answer = input("Install PyArrow for this user now? [y/N]: ").strip().lower()
    if answer != "y":
        print("Parquet export cancelled. Choose another format.")
        return False

    print("Installing PyArrow...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--user", "pyarrow"],
        check=False,
    )
    if result.returncode != 0 or importlib.util.find_spec("pyarrow") is None:
        print("PyArrow could not be installed. Choose another format.")
        return False

    return True


def save_layers(layers, choices, download_dir, extension, geopackage_name, config):
    for choice in choices:
        layer = layers[choice - 1]
        data = prepare_for_export(layer.data, config)

        if extension == ".gpkg" and geopackage_name:
            layer_name = cleaned_name(layer.name)
            data.to_file(
                download_dir / f"{geopackage_name}.gpkg",
                layer=layer_name,
                driver="GPKG",
            )
            print(f"Saved {layer_name} to {geopackage_name}.gpkg.")
            continue

        filename = output_filename(layer, download_dir, extension)
        if extension == ".parquet":
            data.to_parquet(filename)
        else:
            data.to_file(filename)

        print(f"Saved: {filename}")


def prepare_for_export(data, config):
    prepared = data.copy()
    if config.repair_geometry:
        prepared.geometry = shapely.make_valid(prepared.geometry)
    if config.drop_z:
        prepared.geometry = shapely.force_2d(prepared.geometry)
    if config.epsg is not None:
        if prepared.crs is None:
            raise ValueError("Cannot set an output EPSG for data without a CRS.")
        prepared = prepared.to_crs(epsg=config.epsg)
    return prepared


def output_filename(layer, download_dir, extension):
    source_name = layer.download_name or (
        layer.source.split("/")[-1]
        if layer.source.startswith("http")
        else layer.name
    )
    return download_dir / f"{cleaned_name(source_name)}{extension}"


def cleaned_name(name):
    return name.replace("-", "_").replace(" ", "_").replace(":", "_").split(".")[0].lower()

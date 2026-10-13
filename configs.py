from dataclasses import dataclass
import os
from pathlib import Path
import tomllib


@dataclass
class OutputConfig:
    epsg: int | None = None
    repair_geometry: bool = False
    drop_z: bool = False


def config_path():
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_home / "mapier" / "config.toml"


def load_config():
    path = config_path()
    if not path.is_file():
        return OutputConfig()

    with path.open("rb") as file:
        output = tomllib.load(file).get("output", {})

    epsg = output.get("epsg")
    return OutputConfig(
        epsg=epsg if isinstance(epsg, int) and epsg > 0 else None,
        repair_geometry=output.get("repair_geometry") is True,
        drop_z=output.get("drop_z") is True,
    )


def save_config(config):
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["[output]"]
    if config.epsg is not None:
        lines.append(f"epsg = {config.epsg}")
    lines.extend(
        [
            f"repair_geometry = {str(config.repair_geometry).lower()}",
            f"drop_z = {str(config.drop_z).lower()}",
        ]
    )
    path.write_text("\n".join(lines) + "\n")
    return path


def output_summary(config):
    settings = []
    if config.repair_geometry:
        settings.append("repair geometry")
    if config.drop_z:
        settings.append("2D geometry")
    settings.append(f"EPSG:{config.epsg}" if config.epsg else "original CRS")
    return " · ".join(settings)


def configure():
    config = load_config()

    while True:
        print("\nMapier configuration\n")
        print(f"1. Output CRS: {'EPSG:' + str(config.epsg) if config.epsg else 'original CRS'}")
        print(f"2. Repair invalid geometry: {'enabled' if config.repair_geometry else 'disabled'}")
        print(f"3. Drop Z coordinates: {'enabled' if config.drop_z else 'disabled'}")
        print("4. Reset export processing")
        print("0. Save and exit")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            value = input(
                "Output EPSG (e.g. 4674 or EPSG:4674; blank keeps the original CRS): "
            ).strip()
            if not value:
                config.epsg = None
            else:
                try:
                    epsg = int(value.upper().removeprefix("EPSG:").strip())
                    if epsg <= 0:
                        raise ValueError
                    config.epsg = epsg
                except ValueError:
                    print("Enter a positive EPSG number, or leave it blank.")
        elif choice == "2":
            config.repair_geometry = not config.repair_geometry
        elif choice == "3":
            config.drop_z = not config.drop_z
        elif choice == "4":
            config = OutputConfig()
        elif choice == "0":
            path = save_config(config)
            print(f"Configuration saved to {path}.")
            return
        else:
            print("Choose a number from the menu.")

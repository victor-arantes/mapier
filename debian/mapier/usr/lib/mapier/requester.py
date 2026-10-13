import tempfile
from pathlib import Path
import requests
import geopandas as gpd
import pandas as pd
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


def source_name(url):
    parsed = urlparse(url)
    return Path(parsed.path).name or parsed.netloc

def requester(url, headers=None):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        }
    with tempfile.TemporaryDirectory(dir = tempfile.gettempdir()) as tmpdir:
            
            with requests.get(url, stream=True, timeout=120,allow_redirects=True, headers= headers) as r:

                r.raise_for_status()

                size = r.headers.get("Content-Length")
                size_text = (
                    f" ({int(size) / 1024 / 1024:.2f} MB)" if size else ""
                )
                print(f"Downloading {source_name(url)}{size_text}...")

                filename = r.headers.get("Content-Disposition")
                nome_arq = source_name(url)
                if filename:
                    header_name = filename.partition("filename=")[2]
                    nome_arq = header_name.split(";", 1)[0].strip().strip('"') or nome_arq
                local_zip = Path(tmpdir) / nome_arq

                with open(local_zip, "wb") as f:

                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Loading {nome_arq}...")
                result = gpd.read_file(local_zip)
                print(f"Loaded {nome_arq}.")
                return result, nome_arq

def requester2(url, layer):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    params= {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": f"{layer}",
            "outputFormat": "shape-zip",
            "srsName": "EPSG:4674",
        }


    with tempfile.TemporaryDirectory(dir = tempfile.gettempdir()) as tmpdir:
            
            local_zip = Path(tmpdir) / f"{layer.split(':')[-1]}.zip"

            with requests.get(url, stream=True, timeout=120,allow_redirects=True, params= params, headers=headers) as r:

                r.raise_for_status()
                print(f"Downloading WFS layer {layer}...")

                with open(local_zip, "wb") as f:

                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                print(f"Loading WFS layer {layer}...")
                result = gpd.read_file(local_zip)
                print(f"Loaded WFS layer {layer}.")

                return result

def requester3(url):
    params= {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetCapabilities"}
    r = requests.get(url, params=params)

    r.raise_for_status()

    root = ET.fromstring(r.content)
    dic = {}

    for i, feature_type in enumerate(root.findall(".//{http://www.opengis.net/wfs/2.0}FeatureType"), start=1):

        name = feature_type.find("{http://www.opengis.net/wfs/2.0}Name").text
        dic[i] = name

    print("Available WFS layers:")
    for key, value in dic.items():
        print(f"{key}: {value}")

    while True:
        try:
            choices = [choice.strip() for choice in input(
                "Select layers to view (comma-separated numbers, or N to skip): "
            ).split(",")]

            if "N" in (choice.upper() for choice in choices):
                print("No WFS layers selected.")
                return []

            if all(int(choice) in dic for choice in choices):
                choices = list(dict.fromkeys(choices))
                break

            print("Please select listed layer numbers, or N to skip.")

        except ValueError:

            print("Please enter numbers separated by commas.")

    list_of_layers = [dic[int(choice)] for choice in choices]

    return list_of_layers



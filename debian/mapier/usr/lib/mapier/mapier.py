#!/usr/bin/env python3
import sys

from renderer import render_layers
from saver import save_downloaded_layers
from sources import expand_source_lists, load_layers


def main():
    sources = expand_source_lists(sys.argv[1:])
    layers, downloaded_layers = load_layers(sources)
    render_layers(layers)
    save_downloaded_layers(downloaded_layers)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import sys
import time

from configs import configure, load_config
from renderer import render_layers
from saver import save_downloaded_layers
from sources import expand_source_lists, load_layers
from banner import banner

def main():
    arguments = sys.argv[1:]
    if arguments == ["--config"]:
        configure()
        return

    sources = expand_source_lists(arguments)
    config = load_config()
    banner()
    time.sleep(1)
    print("Preparing map…")
    layers, downloaded_layers = load_layers(sources)
    time.sleep(1)
    render_layers(layers)
    save_downloaded_layers(downloaded_layers, config)


if __name__ == "__main__":
    main()

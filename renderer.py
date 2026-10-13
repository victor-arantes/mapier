import base64
from io import BytesIO
import random
import subprocess
import sys

import contextily as ctx
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def render_layers(layers):
    figure, axis = plt.subplots(figsize=(12, 8))
    legend = []

    for layer in layers:
        color = random.choice(list(mcolors.CSS4_COLORS.values()))
        data = layer.data.to_crs(3857)
        data.plot(ax=axis, alpha=0.4, color=color, edgecolor="lime")
        legend.append(
            Patch(facecolor=color, edgecolor="lime", label=layer.name)
        )

    ctx.add_basemap(axis, source=ctx.providers.Esri.WorldImagery)
    axis.set_axis_off()
    axis.legend(handles=legend)

    buffer = BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight", dpi=150)
    subprocess.run(["clear"])
    display_image(buffer.getvalue())
    plt.close(figure)


def display_image(data):
    encoded = base64.standard_b64encode(data)
    chunk_size = 4096

    for start in range(0, len(encoded), chunk_size):
        chunk = encoded[start:start + chunk_size]
        more = start + chunk_size < len(encoded)
        metadata = "a=T,f=100," if start == 0 else ""
        metadata += f"m={1 if more else 0};"
        sys.stdout.buffer.write(
            b"\033_G" + metadata.encode("ascii") + chunk + b"\033\\"
        )

    sys.stdout.flush()

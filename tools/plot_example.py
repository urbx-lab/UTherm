#!/usr/bin/env python3
"""Plot TMRT and masked UTCI from a synthetic-scene output directory."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import rasterio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", type=Path, help="Synthetic scene directory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--band", type=int, default=14, help="1-based forcing band, default 14 (13:00 in the example)")
    args = parser.parse_args()
    figure, axes = plt.subplots(1, 2, figsize=(9, 4), layout="constrained")
    for axis, variable, title in zip(axes, ("TMRT", "UTCI"), ("Mean radiant temperature", "UTCI"), strict=True):
        with rasterio.open(args.scene / "output_folder" / "0_0" / f"{variable}_0_0.tif") as source:
            data = source.read(args.band, masked=True)
            width_m = source.width * abs(source.res[0])
            height_m = source.height * abs(source.res[1])
        axis.set_facecolor("#d9dce2")
        plot = axis.imshow(data, cmap="inferno", extent=(0, width_m, height_m, 0))
        axis.set(title=title, xlabel="East (m)", ylabel="South (m)")
        figure.colorbar(plot, ax=axis, label="°C", shrink=0.75)
    figure.suptitle("Synthetic neighborhood · illustrative summer forcing", fontsize=12)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()

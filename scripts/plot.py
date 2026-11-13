"""
plot.py - draws the scatter plot from the CSV file written by the C++ program.

This script does NO statistics. It only reads the CSV and draws.

Usage:
    python plot.py <csv_path> <png_path> <mean> <lower_limit> <upper_limit>
"""

import csv
import sys

import matplotlib
matplotlib.use("Agg")  # draw to a file, no window needed
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def main():
    csv_path = sys.argv[1]
    png_path = sys.argv[2]
    mean = float(sys.argv[3])
    lower_limit = float(sys.argv[4])
    upper_limit = float(sys.argv[5])

    # Read the CSV into separate lists (normal points and outlier points)
    normal_x, normal_y = [], []
    outlier_x, outlier_y = [], []

    with open(csv_path) as file:
        for row in csv.DictReader(file):
            x = int(row["index"])
            y = float(row["value"])
            if row["status"] == "Outlier":
                outlier_x.append(x)
                outlier_y.append(y)
            else:
                normal_x.append(x)
                normal_y.append(y)

    fig, ax = plt.subplots(figsize=(9, 4.6))

    # Reference lines calculated by the C++ program
    ax.axhline(mean, color="#64748B", linewidth=1.2, label="Mean")
    ax.axhline(upper_limit, color="#94A3B8", linewidth=1, linestyle="--",
               label="Mean ± 3 SD")
    ax.axhline(lower_limit, color="#94A3B8", linewidth=1, linestyle="--")

    # Normal points (blue) and outliers (red, bigger)
    ax.scatter(normal_x, normal_y, color="#2563EB", s=55, label="Normal", zorder=3)
    ax.scatter(outlier_x, outlier_y, color="#DC2626", s=110, marker="D",
               edgecolors="white", linewidths=1.2, label="Outlier", zorder=4)

    ax.set_title("Data points and outliers (Z-Score method)", fontsize=13, pad=12)
    ax.set_xlabel("Observation number")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # whole numbers only
    ax.set_ylabel("Value")
    ax.grid(True, color="#E2E8F0", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="center right")

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    fig.tight_layout()
    fig.savefig(png_path, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()

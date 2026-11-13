"""
app.py - Flask backend.

Flask does only three things:
  1. Validates the user's input
  2. Runs the C++ program (which does ALL the statistics) and the plot script
  3. Sends the results back to the browser

No statistics are calculated in Python.
"""

import csv
import math
import os
import subprocess
import sys
import time

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ---- File locations ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CPP_SOURCE = os.path.join(BASE_DIR, "src", "outlier.cpp")
CPP_PROGRAM = os.path.join(BASE_DIR, "src", "outlier")
PLOT_SCRIPT = os.path.join(BASE_DIR, "scripts", "plot.py")
CSV_PATH = os.path.join(BASE_DIR, "output", "results.csv")
PLOT_PATH = os.path.join(BASE_DIR, "static", "plot.png")

MAX_VALUES = 5000      # keep the page fast
MAX_ABS_VALUE = 1e100  # avoid overflow when squaring inside C++


def compile_cpp_if_needed():
    """Compile src/outlier.cpp the first time (or if the source changed)."""
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    needs_compile = (not os.path.exists(CPP_PROGRAM)
                     or os.path.getmtime(CPP_SOURCE) > os.path.getmtime(CPP_PROGRAM))
    if needs_compile:
        print("Compiling C++ program...")
        result = subprocess.run(["g++", "-o", CPP_PROGRAM, CPP_SOURCE],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr)
            sys.exit("C++ compilation failed. See the message above.")


def validate_input(text):
    """Turn the text '10, 12, 11' into a list of numbers.
    Returns (numbers, error_message). One of them is always None."""
    if not text or not text.strip():
        return None, "Please enter some numbers separated by commas."

    numbers = []
    for item in text.split(","):
        item = item.strip()
        if item == "":
            return None, "Found an empty value. Check for double or trailing commas."
        try:
            number = float(item)
        except ValueError:
            return None, f"'{item}' is not a valid number. Use only numbers separated by commas."
        if not math.isfinite(number):
            return None, f"'{item}' is not a valid number."
        if abs(number) > MAX_ABS_VALUE:
            return None, f"'{item}' is too large. Keep values below 1e100."
        numbers.append(number)

    if len(numbers) < 2:
        return None, "Please enter at least 2 numbers."
    if len(numbers) > MAX_VALUES:
        return None, f"Too many values. The limit is {MAX_VALUES}."
    return numbers, None


def run_cpp(numbers):
    """Send numbers to the C++ program and read its summary output."""
    numbers_text = " ".join(repr(n) for n in numbers)
    result = subprocess.run([CPP_PROGRAM, CSV_PATH], input=numbers_text,
                            capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        return None, result.stderr.strip() or "The C++ program failed."

    summary = {}
    for line in result.stdout.splitlines():
        key, value = line.split("=")
        summary[key] = value
    return summary, None


def read_csv_rows():
    """Read the CSV written by C++ so the browser can show it in a table."""
    with open(CSV_PATH) as file:
        return list(csv.DictReader(file))


def make_plot(summary):
    """Run scripts/plot.py to draw the graph from the CSV."""
    result = subprocess.run(
        [sys.executable, PLOT_SCRIPT, CSV_PATH, PLOT_PATH,
         summary["mean"], summary["lower_limit"], summary["upper_limit"]],
        capture_output=True, text=True, timeout=30)
    return result.returncode == 0


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    numbers, error = validate_input(data.get("data", ""))
    if error:
        return jsonify({"error": error}), 400

    summary, error = run_cpp(numbers)
    if error:
        return jsonify({"error": error}), 500

    if not make_plot(summary):
        return jsonify({"error": "Could not generate the graph."}), 500

    return jsonify({
        "count": summary["count"],
        "mean": summary["mean"],
        "std": summary["std"],
        "outliers": summary["outliers"],
        "zero_std": summary["zero_std"] == "1",
        "rows": read_csv_rows(),
        "plot_url": "/static/plot.png?t=" + str(int(time.time() * 1000)),
    })


if __name__ == "__main__":
    compile_cpp_if_needed()
    # Port 5001 because macOS uses port 5000 for AirPlay Receiver
    app.run(debug=False, port=5001)

"""Generate reviewable portfolio copy from a verified synthetic forecast run."""

import argparse
import json
from pathlib import Path


METHODS = {
    "seasonal_naive": "seasonal-naïve",
    "ar1": "component AR(1)",
    "ridge_var": "ridge VAR",
}


def build_pack(results: Path, output: Path, source_url: str) -> None:
    metadata = json.loads((results / "run_metadata.json").read_text(encoding="utf-8"))
    if metadata.get("synthetic") is not True:
        raise ValueError("Only synthetic demo runs are supported for public portfolio copy.")
    for name in ("forecast_evaluation.svg", "test_metrics.csv"):
        if not (results / name).is_file():
            raise FileNotFoundError(results / name)

    selected = METHODS[metadata["selected_method"]]
    rows = int(metadata["rows"])
    horizon = int(metadata["horizon"])
    test_origins = int(metadata["test_origin_count"])
    body = f"""# Portfolio review pack

## LinkedIn draft

What happens when external-sector forecasts have to add up?

In a public Python demo, I compared seasonal-naïve, component AR(1), and ridge VAR forecasts. The models forecast the underlying components, then reconcile current-account and reserve flows.

The example uses {rows} synthetic quarterly observations and a {horizon}-quarter horizon. The earlier validation window selected the {selected} method. That choice was frozen before evaluating {test_origins} later test origins, so we could see how the original decision held up without changing it after the fact.

The chart illustrates the workflow on synthetic data. It does not measure historical forecast accuracy for India.

Code and methods: {source_url}

**Chart alt text:** Line chart comparing observed synthetic current-account values with forecasts from the frozen {selected} method over the later test period.

## Résumé bullet draft

Built a Python demonstration that compares seasonal-naïve, component AR(1), and ridge VAR forecasts, evaluates the frozen model choice on later test data, and reconciles current-account and reserve flows using synthetic data.

## Evidence to check before publishing

- Run metadata: `run_metadata.json`
- Later-test metrics: `test_metrics.csv`
- Chart: `forecast_evaluation.svg`
- Commit and source: {source_url}

This file is a draft for review. The workflow only generates and uploads files.
"""
    output.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-url", required=True)
    args = parser.parse_args()
    build_pack(args.results, args.output, args.source_url)

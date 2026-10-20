![India External-Sector Forecasting](assets/header.svg)

# India External-Sector Forecasting

Component-coherent current-account and reserve-flow forecasts with seasonal-naive, AR1 and ridge-VAR comparisons on synthetic data.

**Research question:** Can component-based forecasts preserve external-sector accounting identities while competing with transparent time-series benchmarks?

**Public edition:** New synthetic forecasting demonstration, distinct from the original MAAKRO code, data and reports.

**10 functional checks passed locally**, plus a complete demonstration run.

See [the original research scope](docs/RESEARCH_SCOPE.md) for the distinction between the broader collaborative project and this public implementation.

Read the [original research publication status](docs/ORIGINAL_RESEARCH_STATUS.md) for the larger held source and data bundle.

## What you can inspect

- Forecast seven components rather than independently forecasting incompatible aggregates.
- Compare seasonal naive, component AR1 and a standardized ridge VAR with fixed penalty.
- Use expanding training samples and nonoverlapping four-quarter evaluation blocks.
- Choose a method using an early validation period with a two-percent benchmark-improvement safeguard.
- Freeze that choice before the later test period and reconcile current account and reserve transactions exactly.

## Results preview

All values below are synthetic or illustrative workflow results.

![India External-Sector Forecasting results preview](demo_output/forecast_evaluation.svg)

| Method | Later-test MAE | Later-test RMSE | MASE | Frozen selection |
| --- | --- | --- | --- | --- |
| ar1 | 2624.82 | 3264.55 | 0.935607 | False |
| ridge_var | 2625.1 | 3191.02 | 0.93586 | False |
| seasonal_naive | 3096.27 | 3658.24 | 1.10157 | True |

Validation selected **seasonal_naive**. On this seeded later test, other candidates can score better. The earlier selection is retained, preserving the distinction between model selection and honest later evaluation. Final point forecasts are in forecast_components.csv.

## Run the example

Use Python 3.12. From this project's directory:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -v
python forecast_demo.py --demo --output demo_output
```

For an isolated environment, run `python -m venv .venv` first. Activate it with `source .venv/bin/activate` on Linux/macOS or `.venv\Scripts\activate` on Windows. The standard example runs offline after dependencies are installed.

The [notebook walkthrough](notebooks/01_results_walkthrough.ipynb) explains the saved outputs. Exact command-line options appear in [CLI.txt](docs/CLI.txt).

## Documentation

| Guide | What it covers |
| --- | --- |
| [Methods](docs/METHODS.md) | Formulas, assumptions and interpretation |
| [Data dictionary](docs/DATA_DICTIONARY.md) | Variables, units and validation rules |
| [Results](docs/RESULTS.md) | Actual bundled output and how to read it |
| [Reproducibility](REPRODUCIBILITY.md) | Commands, checks and the recorded environment |
| [Provenance and attribution](docs/PROVENANCE.md) | Historical context, reconstruction and contribution |
| [Roadmap](docs/ROADMAP.md) | Specific extensions, with unfinished work labelled |
| [References](docs/REFERENCES.md) | Method documentation and source links |

## Limits of interpretation

- The 104-quarter public example is synthetic and differs from the original 105-quarter research sample.
- A current-vintage real-data replacement would remain retrospective unless genuine historical vintages were supplied.
- The frozen selected method can lose to another method on later test data.
- No calibrated prediction interval, causal policy effect or real-time accuracy claim is made.

## Contribution and research context

GIPE Group 5 current-account sustainability work, with a forty-quarter descriptive assessment and a 105-quarter original forecasting rebuild.

Arinjai Das served as team lead and contributed to empirical work, ratios and reserves analysis, and project coordination. An earlier original package passed 821 local checks; the newer supplied revision passed 622 independent numerical checks and 13 principal output files matched byte for byte locally. These are separate check sets on held empirical packages, not public CI results. The new public demonstration has its own code, data and checks.

**Skills demonstrated:** Python, time-series forecasting, chronological validation, benchmarks, ridge VAR, accounting reconciliation.

[Portfolio](https://github.com/arinjaidas/My-Projects) · [GitHub profile](https://github.com/arinjaidas)

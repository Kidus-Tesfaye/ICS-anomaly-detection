# ics-anomaly-detection

Lightweight anomaly detection for industrial control system (ICS) traffic for statistical, shallow-ML, and tiny-NN
detectors on open ICS datasets.


[![CI](https://github.com/Kidus-Tesfaye/ICS-anomaly-detection/actions/workflows/ci.yml/badge.svg)](https://github.com/Kidus-Tesfaye/ICS-anomaly-detection/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)

## Why

Attacks on industrial control systems are rising, but most published detectors are heavy deep
models that are impractical on edge gateways, and recent rigorous evaluations show simple
baselines are often competitive with them. What's missing is a map of the
efficiency-vs-detection trade-off across model families on a shared open dataset, under a
rigorous metric protocol. This project aims to address this gap. 

## Quickstart

```bash
git clone https://github.com/Kidus-Tesfaye/ICS-anomaly-detection
cd ics-anomaly-detection

# with uv (recommended)
uv sync --extra dev
uv run pytest

# or with plain pip
python -m venv .venv
.venv/Scripts/activate        # Windows; use .venv/bin/activate on Linux/macOS
pip install -e ".[dev]"
pytest
```

Dataset download, training, and benchmarking commands land in Milestones 2–6
(`make data` / `make train` / `make bench` / `make reproduce`).

## Repository structure

```
configs/          # YAML configs: one per dataset, model, experiment
src/ics_anomaly/  # installable package: data, features, models, eval, deploy, viz
tests/            # unit, data-validation (leakage!), and toy end-to-end integration tests
docs/             # data card, literature review, architecture decision records
results/          # committed metrics, figures, raw benchmark logs
notebooks/        # exploration only — never the source of truth
```

## Methodology

Reproduce a credible deep baseline (LSTM-AE/USAD) on HAI → implement 3–5 lightweight detectors
(PCA reconstruction, Isolation Forest, CUSUM/EWMA, tiny autoencoder) behind one config-driven
interface → evaluate all of them on an identical, block-split, leakage-tested protocol with
point-wise and range-aware (eTaPR) metrics plus time-to-detection → convert everything to
ONNX and benchmark single-threaded constrained-CPU latency/memory/size → publish the Pareto
frontier.

## Limitations

- Resource numbers are constrained-CPU estimates, not on-device measurements (real edge
  hardware is future work).
- Raw datasets are license-restricted and never redistributed here; see `docs/data_card.md`
  for access instructions and checksums.

## License & citation

MIT — see [LICENSE](LICENSE). If you use this work, please cite via [CITATION.cff](CITATION.cff).

# Convenience targets. On Windows without make, run the underlying commands directly
# (they are all plain python/uv invocations — see README Quickstart).

.PHONY: install lint typecheck test check-bib data train bench reproduce

install:
	uv sync --extra dev

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy

test:
	uv run pytest

check-bib:  ## validate docs/*.bib after every Zotero re-export
	uv run python scripts/check_bibliography.py

# --- Placeholders wired up in later milestones ---

data:       ## M2: download + verify + preprocess HAI
	@echo "TODO(M2): scripts/download_data.py + preprocessing" && exit 1

train:      ## M3/M4: train detectors from configs/experiment/*.yaml
	@echo "TODO(M3): scripts/train.py --config configs/experiment/..." && exit 1

bench:      ## M6: ONNX conversion + constrained-CPU benchmark
	@echo "TODO(M6): scripts/bench.py" && exit 1

reproduce:  ## M5+: regenerate the headline Pareto figure end-to-end
	@echo "TODO(M5): data -> train -> eval -> plot" && exit 1

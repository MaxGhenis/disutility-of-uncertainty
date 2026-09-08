# Reproducible model and Quarto paper commands.
UV ?= uv
PYTHON ?= 3.13.9
LOCKED_UV = env -u UV_FROZEN $(UV)
RUN = $(UV) run --no-sync

.PHONY: help install test test-quick test-policyengine lint format generate figures check-results paper pdf latex serve deploy clean replicate check-all myst watch venv activate dev build-all paper-stats check-citations

help:
	@echo "make install          Install the locked development and paper environment"
	@echo "make test             Run fast tests (live PolicyEngine is opt-in)"
	@echo "make test-policyengine  Run optional live PolicyEngine validation"
	@echo "make generate         Recompute results, paper includes, and figures"
	@echo "make check-results    Check committed outputs against recomputed results"
	@echo "make paper / pdf      Generate inputs and render HTML / PDF"
	@echo "make serve            Generate inputs and preview the paper"
	@echo "make replicate        Generate results and render HTML and PDF"
	@echo "make clean            Remove this project's build artifacts"

install:
	$(LOCKED_UV) sync --python $(PYTHON) --locked --extra dev --extra paper
	@command -v quarto >/dev/null || echo "Install Quarto 1.9.36 separately to render the paper."

test:
	$(RUN) pytest tests/ -v

test-quick:
	$(RUN) pytest tests/ -q --no-cov

test-policyengine:
	$(LOCKED_UV) sync --python $(PYTHON) --locked --extra dev --extra policyengine
	$(RUN) pytest tests/ -v --run-policyengine -m policyengine

lint:
	$(RUN) flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	$(RUN) black --check src tests
	$(RUN) isort --check-only src tests
	$(RUN) mypy src

format:
	$(RUN) isort src tests
	$(RUN) black src tests

generate:
	$(RUN) python -m taxuncertainty.pipeline

figures: generate

check-results:
	$(RUN) python -m taxuncertainty.pipeline --check

paper: generate
	cd paper && quarto render index.qmd --to html

pdf: generate
	cd paper && quarto render index.qmd --to pdf

latex: generate
	cd paper && quarto render index.qmd --to latex

serve: generate
	cd paper && quarto preview index.qmd

deploy: generate
	cd paper && quarto publish gh-pages

# Backward-compatible name for the previous renderer.
myst: paper

replicate: paper pdf
	@echo "Results and paper inputs regenerated; rendered artifacts are in paper/_build/."

# Restrict recursive cleanup to project output/source paths, preserving .venv.
clean:
	rm -rf paper/_build paper/.quarto build dist .pytest_cache .coverage htmlcov .mypy_cache
	find src tests -type d \( -name __pycache__ -o -name '*.egg-info' \) -prune -exec rm -rf {} +
	find src tests -type f -name '*.pyc' -delete

check-all: lint test check-results paper

watch:
	@echo "Watching source and paper files (requires fswatch)..."
	@fswatch -o --exclude='__pycache__' --exclude='data/results\.json' src paper/chapters paper/index.qmd paper/_quarto.yml paper/references.bib | xargs -n1 -I{} make paper

venv: install

activate:
	@echo "Run: source .venv/bin/activate"

dev: serve

build-all: check-all pdf

paper-stats:
	@find paper -path "paper/_build" -prune -o \( -name "*.md" -o -name "*.qmd" \) -print | xargs wc -w
	@rg -c '^@' paper/references.bib

check-citations:
	@$(RUN) python -c 'import re; from pathlib import Path; paper_files=[Path("paper/index.qmd"), *sorted(Path("paper/chapters").glob("*.md"))]; bib_text=Path("paper/references.bib").read_text(); bib_keys=set(re.findall(r"@\w+\{([^,]+),", bib_text)); citation_keys=set(); [citation_keys.update(re.findall(r"@([A-Za-z0-9:_-]+)", path.read_text())) for path in paper_files]; ignore_prefixes=("tbl-", "fig-", "sec-", "eq-", "lem-", "thm-", "cor-"); missing=sorted(key for key in citation_keys if key not in bib_keys and not key.startswith(ignore_prefixes)); [print(f"Missing citation: @{key}") for key in missing]; raise SystemExit(1 if missing else 0)'

.DEFAULT_GOAL := help

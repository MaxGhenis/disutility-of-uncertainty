# Makefile for Tax Uncertainty Analysis Project

.PHONY: help install test test-quick serve clean pdf deploy lint format check-all paper myst replicate latex watch

# Default target
help:
	@echo "Tax Uncertainty Analysis - Make Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install     Install full reproducible stack (code + empirical + paper)"
	@echo "  make test        Run test suite with coverage"
	@echo "  make lint        Run code quality checks"
	@echo "  make format      Auto-format code with black"
	@echo ""
	@echo "Book/Paper:"
	@echo "  make paper       Build the Quarto HTML paper"
	@echo "  make serve       Start the Quarto preview server"
	@echo "  make pdf         Generate PDF output"
	@echo "  make figures     Generate analysis figures (blocks 1–4)"
	@echo "  make deploy      Deploy to GitHub Pages"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       Remove build artifacts"
	@echo "  make check-all   Run all checks (lint, test, build)"

# Install dependencies
install:
	pip install -e ".[dev,research,policyengine]"
	@command -v quarto >/dev/null || \
		echo "Install the Quarto CLI separately to build the paper."

# Run tests
test:
	pytest tests/ -v --cov=src/taxuncertainty --cov-report=term-missing --cov-report=html

# Quick test without coverage
test-quick:
	pytest tests/ -v

# Lint code
lint:
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	mypy src

# Format code
format:
	black src tests
	isort src tests

# Build Quarto paper (HTML)
paper:
	cd paper && quarto render index.qmd --to html
	@echo "Quarto paper available at: paper/_build/index.html"

# Backward-compatible alias for the old target name
myst: paper

# Generate results via pipeline
figures:
	PYTHONPATH=src python3 -c "from taxuncertainty.pipeline import generate_results; generate_results()"

# End-to-end replication (pipeline + paper)
replicate: clean figures paper pdf
	@echo "Replication artifacts in src/taxuncertainty/data/results.json and paper/_build/"

# Serve with Quarto (development)
serve:
	cd paper && quarto preview index.qmd

# Generate PDF
pdf:
	cd paper && quarto render index.qmd --to pdf
	@echo "PDF generated at: paper/_build/index.pdf"

# Build LaTeX
latex:
	cd paper && quarto render index.qmd --to latex
	@echo "LaTeX generated at: paper/_build/index.tex"

# Deploy to GitHub Pages
deploy:
	cd paper && quarto publish gh-pages

# Clean build artifacts
clean:
	rm -rf paper/_build
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete

# Run all checks
check-all: lint test paper
	@echo "All checks passed!"

# Watch for changes and rebuild (requires fswatch on macOS)
watch:
	@echo "Watching for changes..."
	@fswatch -o src paper | xargs -n1 -I{} make paper

# Create GitHub PR
pr:
	gh pr create --fill

# Development workflow shortcuts
dev: serve
	@echo "Development server started"

build-all: clean install test paper pdf
	@echo "Full build completed"

# Paper submission helpers
paper-stats:
	@echo "Paper Statistics:"
	@echo "----------------"
	@find paper -path "paper/_build" -prune -o \( -name "*.md" -o -name "*.qmd" -o -name "*.ipynb" \) -print | xargs wc -w
	@echo ""
	@echo "Bibliography entries:"
	@grep -c "@" paper/references.bib

check-citations:
	@echo "Checking citations..."
	@python3 -c 'import re; from pathlib import Path; paper_files=[Path("paper/index.qmd"), *sorted(Path("paper/chapters").glob("*.md"))]; bib_text=Path("paper/references.bib").read_text(); bib_keys=set(re.findall(r"@\w+\{([^,]+),", bib_text)); citation_keys=set(); [citation_keys.update(re.findall(r"@([A-Za-z0-9:_-]+)", path.read_text())) for path in paper_files]; ignore_prefixes=("tbl-", "fig-", "sec-", "eq-", "lem-", "thm-", "cor-"); missing=sorted(key for key in citation_keys if key not in bib_keys and not key.startswith(ignore_prefixes)); [print(f"Missing citation: @{key}") for key in missing]; raise SystemExit(1 if missing else 0)'

# Docker support (optional)
docker-build:
	docker build -t tax-uncertainty .

docker-run:
	docker run -p 3001:3001 -v $$(pwd):/app tax-uncertainty

# Virtual environment management
venv:
	python -m venv .venv
	./.venv/bin/pip install -e ".[dev,research,policyengine]"

activate:
	@echo "Run: source .venv/bin/activate"

.DEFAULT_GOAL := help

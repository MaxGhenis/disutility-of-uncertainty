# Makefile for Tax Uncertainty Analysis Project

.PHONY: help install test build serve clean pdf deploy lint format check-all

# Default target
help:
	@echo "Tax Uncertainty Analysis - Make Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install     Install all dependencies (package + book)"
	@echo "  make test        Run test suite with coverage"
	@echo "  make lint        Run code quality checks"
	@echo "  make format      Auto-format code with black"
	@echo ""
	@echo "Book/Paper:"
	@echo "  make book        Build Jupyter Book (legacy)"
	@echo "  make myst        Build with MyST (next-gen)"
	@echo "  make serve       Start MyST dev server (port 3001)"
	@echo "  make pdf         Generate PDF output"
	@echo "  make figures     Generate analysis figures (blocks 1–4)"
	@echo "  make deploy      Deploy to GitHub Pages"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       Remove build artifacts"
	@echo "  make check-all   Run all checks (lint, test, build)"

# Install dependencies
install:
	pip install -e ".[dev,research]"
	pip install mystmd jupyter-book

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

# Build Jupyter Book (legacy)
book:
	cd paper && jupyter-book build . --builder html
	@echo "Book available at: paper/_build/html/index.html"

# Build with MyST (recommended)
myst: figures
	cd paper && myst build
	@echo "MyST book available at: paper/_build/site/index.html"

# Generate analysis figures and CSVs (blocks 1–4)
figures:
	mkdir -p paper/figures
	PYTHONPATH=src python3 scripts/run_analysis.py --outdir paper/figures --seed 42 --grid 101 --pop-n 1000 --opt-tax-grid 31 --opt-sd-n 5 --tax-n 30

# End-to-end replication (figures + book)
replicate: clean figures myst
	@echo "Replication artifacts in paper/figures and paper/_build/site"

# Serve with MyST (development)
serve:
	cd paper && myst start
	@echo "Server running at: http://localhost:3001"

# Generate PDF
pdf:
	cd paper && myst build --pdf
	@echo "PDF generated at: paper/_build/exports/tax-uncertainty.pdf"

# Build LaTeX
latex:
	cd paper && myst build --tex
	@echo "LaTeX generated at: paper/_build/exports/tax-uncertainty.tex"

# Deploy to GitHub Pages
deploy:
	cd paper && myst build --gh-pages

# Clean build artifacts
clean:
	rm -rf paper/_build
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete

# Clean notebooks
clean-notebooks:
	jupyter nbconvert --clear-output --inplace paper/chapters/*.ipynb

# Execute notebooks
execute-notebooks:
	cd paper && jupyter-book execute chapters/theoretical_framework.ipynb
	cd paper && jupyter-book execute chapters/baseline_results.ipynb

# Run all checks
check-all: lint test myst
	@echo "All checks passed!"

# Watch for changes and rebuild (requires fswatch on macOS)
watch:
	@echo "Watching for changes..."
	@fswatch -o src paper | xargs -n1 -I{} make myst

# Create GitHub PR
pr:
	gh pr create --fill

# Git operations
commit:
	git add -A
	git commit -m "Update tax uncertainty analysis"

push:
	git push origin feature/tax-uncertainty-analysis

# Development workflow shortcuts
dev: serve
	@echo "Development server started"

build-all: clean install test myst pdf
	@echo "Full build completed"

# Paper submission helpers
paper-stats:
	@echo "Paper Statistics:"
	@echo "----------------"
	@find paper/chapters -name "*.md" -o -name "*.ipynb" | xargs wc -w
	@echo ""
	@echo "Bibliography entries:"
	@grep -c "@" paper/references.bib

check-citations:
	@echo "Checking citations..."
	@for cite in $$(grep -oh "@\w\+" paper/chapters/*.md | sort -u); do \
		grep -q "$$cite" paper/references.bib || echo "Missing citation: $$cite"; \
	done

# Docker support (optional)
docker-build:
	docker build -t tax-uncertainty .

docker-run:
	docker run -p 3001:3001 -v $$(pwd):/app tax-uncertainty

# Virtual environment management
venv:
	python -m venv venv
	./venv/bin/pip install -e ".[dev,research]"

activate:
	@echo "Run: source venv/bin/activate"

.DEFAULT_GOAL := help

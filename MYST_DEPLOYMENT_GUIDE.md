# Complete Guide to Deploying MyST Content to GitHub Pages

This comprehensive guide provides everything needed to deploy MyST (Markedly Structured Text) content to GitHub Pages using the modern MyST build system from next.jupyterbook.org.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Configuration Files](#configuration-files)
3. [GitHub Actions Workflow](#github-actions-workflow)
4. [Dependencies Setup](#dependencies-setup)
5. [Critical Files](#critical-files)
6. [GitHub Settings](#github-settings)
7. [Common Pitfalls](#common-pitfalls)
8. [Testing and Development](#testing-and-development)
9. [Makefile Recipes](#makefile-recipes)

## Project Structure

Your repository should follow this structure:

```
your-repo/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Main CI/CD workflow
│       └── deploy-preview.yml  # Optional: PR previews
├── paper/                      # MyST content directory
│   ├── myst.yml               # MyST configuration
│   ├── index.md               # Main landing page
│   ├── references.bib         # Bibliography
│   ├── .nojekyll              # Critical for GitHub Pages
│   ├── chapters/              # Content chapters
│   │   ├── introduction.md
│   │   ├── methodology.ipynb
│   │   └── ...
│   ├── figures/               # Static figures
│   ├── tables/                # Data tables
│   └── _build/                # Build output (gitignored)
├── src/                       # Optional: Python package
├── tests/                     # Optional: Test suite
├── pyproject.toml             # Python dependencies
├── Makefile                   # Build recipes
├── .gitignore
└── README.md
```

**Key Points:**
- MyST content lives in a dedicated directory (`paper/` in this example)
- The `.nojekyll` file must be in the source content directory
- Build outputs go in `_build/` and should be gitignored

## Configuration Files

### MyST Configuration (`paper/myst.yml`)

```yaml
version: 1
project:
  title: Your Project Title
  authors:
    - name: Your Name
      email: your.email@domain.com
  copyright: '2024'
  github: username/repository-name
  
  # Optional: Interactive computing with Thebe/Binder
  thebe:
    binder:
      repo: username/repository-name
      provider: github
      url: https://mybinder.org
      ref: main
  
  # Bibliography
  bibliography:
    - references.bib
  
  # Export formats
  exports:
    - format: pdf
      template: plain_latex_book
      output: exports/your-project.pdf

  # Table of contents structure
  toc:
    - file: index.md
    - title: Introduction
      children:
        - file: chapters/introduction.md
    - title: Methodology  
      children:
        - file: chapters/theoretical_framework.ipynb
        - file: chapters/empirical_approach.md
    # Add more sections as needed

# Site configuration
site:
  options:
    logo: ''                    # Optional: path to logo
    folders: true              # Enable folder navigation
  template: book-theme         # Use MyST book theme
```

### Python Dependencies (`pyproject.toml`)

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "your-project-name"
version = "0.1.0"
description = "Your project description"
readme = "README.md"
requires-python = ">=3.13"
authors = [
    {name = "Your Name"},
]
license = {text = "MIT"}

dependencies = [
    "numpy>=1.21.0",
    "pandas>=1.3.0",
    "scipy>=1.7.0",
    "matplotlib>=3.4.0",
    "plotly>=5.0.0",
    "jupyter-book>=0.15.0",
    "sphinx>=4.0.0",
    # Add your specific dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0",
    "mypy>=0.950",
]

research = [
    "jupyterlab>=3.4.0",
    "notebook>=6.4.0",
    "ipywidgets>=7.7.0",
]
```

## GitHub Actions Workflow

### Main CI/CD Workflow (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [ main, feature/* ]
  pull_request:
    branches: [ main ]

# CRITICAL: These permissions are required for GitHub Pages deployment
permissions:
  contents: read
  pages: write
  id-token: write

# Allow only one concurrent deployment
concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=term
    
    - name: Lint code
      run: |
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics

  build-book:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    # IMPORTANT: Use current versions
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '22'
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[research]"
        npm install -g mystmd
    
    # Execute notebooks if needed
    - name: Execute notebooks
      run: |
        cd paper
        # Execute any computational notebooks
        # jupyter nbconvert --to notebook --execute --inplace chapters/*.ipynb
    
    - name: Build MyST Book
      run: |
        cd paper
        myst build --html
        # CRITICAL: Ensure .nojekyll file is present
        touch _build/html/.nojekyll
    
    - name: Upload book artifact
      uses: actions/upload-artifact@v4
      with:
        name: myst-book
        path: paper/_build/html/
    
    # Only deploy from main branch pushes
    - name: Setup Pages
      if: github.ref == 'refs/heads/main' && github.event_name == 'push'
      uses: actions/configure-pages@v5
      
    - name: Upload Pages artifact
      if: github.ref == 'refs/heads/main' && github.event_name == 'push'
      uses: actions/upload-pages-artifact@v3
      with:
        path: paper/_build/html

  # Deployment job - runs only on main branch pushes
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build-book
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Optional: PR Preview Workflow (`.github/workflows/deploy-preview.yml`)

```yaml
name: Deploy PR Preview

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    if: github.event.pull_request.head.repo.full_name == github.repository
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '22'
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[research]"
        npm install -g mystmd
    
    - name: Build MyST Book
      run: |
        cd paper && myst build --html
    
    # Deploy to Netlify (requires NETLIFY_AUTH_TOKEN and NETLIFY_SITE_ID secrets)
    - name: Deploy Preview to Netlify
      uses: nwtgck/actions-netlify@v3.0
      with:
        publish-dir: 'paper/_build/html'
        production-deploy: false
        github-token: ${{ secrets.GITHUB_TOKEN }}
        deploy-message: "Deploy PR Preview ${{ github.event.pull_request.number }}"
        enable-pull-request-comment: true
        enable-commit-comment: false
        overwrites-pull-request-comment: true
        alias: pr-${{ github.event.pull_request.number }}
      env:
        NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
        NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
      if: env.NETLIFY_AUTH_TOKEN != ''
```

## Dependencies Setup

The workflow installs MyST via npm and Python dependencies via pip:

```bash
# MyST installation (globally via npm)
npm install -g mystmd

# Python dependencies (via pyproject.toml)
pip install -e ".[research]"
```

**Key packages:**
- `mystmd`: The MyST build system
- `jupyter-book`: Legacy Jupyter Book (for compatibility)
- `sphinx`: Documentation builder
- Computing libraries: `numpy`, `pandas`, `scipy`, `matplotlib`, `plotly`

## Critical Files

### 1. `.nojekyll` File

**Location:** `paper/.nojekyll` (in your content directory)

```bash
# Create the file (empty is fine)
touch paper/.nojekyll
```

**Why it's critical:**
- GitHub Pages uses Jekyll by default
- Jekyll ignores files/folders starting with `_` (like `_static`)
- MyST builds create `_static` folders for CSS/JS
- Without `.nojekyll`, your site will have broken styling and functionality

### 2. `.gitignore` Entries

```gitignore
# MyST build outputs
paper/_build/

# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
.pytest_cache/
.coverage
htmlcov/

# Jupyter
.ipynb_checkpoints

# Environment
.env
.venv
venv/
```

## GitHub Settings

### After First Deployment

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select **"GitHub Actions"** (not "Deploy from branch")
4. Your site will be available at `https://username.github.io/repository-name/`

### Branch Protection (Optional)

For production repositories, consider:
1. **Settings** → **Branches**
2. Add rule for `main` branch
3. Enable "Require status checks to pass before merging"
4. Select your CI workflow checks

## Common Pitfalls

### 1. Missing `.nojekyll` File

**Symptom:** Site loads but has no CSS styling, JavaScript doesn't work
**Solution:** Ensure `.nojekyll` exists in your source directory AND gets copied to build output

```yaml
# In GitHub Actions workflow
- name: Build MyST Book
  run: |
    cd paper
    myst build --html
    touch _build/html/.nojekyll  # Ensure it's in output
```

### 2. Wrong Permissions

**Symptom:** "Deploy to GitHub Pages" step fails with permission errors
**Solution:** Verify workflow permissions:

```yaml
permissions:
  contents: read
  pages: write        # Required for deployment
  id-token: write     # Required for authentication
```

### 3. Using Outdated Actions

**Symptom:** Workflow fails with deprecation warnings or errors
**Solution:** Use current versions:

```yaml
- uses: actions/checkout@v4              # Not v3
- uses: actions/setup-node@v4            # Not v3
- uses: actions/setup-python@v5          # Not v4
- uses: actions/configure-pages@v5       # Latest
- uses: actions/upload-pages-artifact@v3 # Latest
- uses: actions/deploy-pages@v4          # Latest
```

### 4. Path Issues

**Symptom:** GitHub Actions can't find files or builds fail
**Solution:** Always specify working directory:

```yaml
- name: Build MyST Book
  run: |
    cd paper                    # Change to content directory
    myst build --html
```

### 5. Node.js/Python Version Mismatch

**Symptom:** Installation or build failures
**Solution:** Use current stable versions:

```yaml
- name: Set up Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '22'        # Current LTS

- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.13'    # Current stable
```

## Testing and Development

### Local Development

```bash
# Install dependencies
make install

# Start development server (auto-rebuilds on changes)
cd paper && myst start

# Manual build
cd paper && myst build --html

# View locally built site
open paper/_build/html/index.html
```

### Makefile Target

Add this to your `Makefile`:

```makefile
# Serve with MyST (development)
serve:
	cd paper && myst start
	@echo "Server running at: http://localhost:3001"

# Build with MyST 
build:
	cd paper && myst build --html
	@echo "Site built in: paper/_build/html/"

# Deploy to GitHub Pages (local)
deploy:
	cd paper && myst build --gh-pages
```

## Makefile Recipes

Here's a complete `Makefile` for MyST projects:

```makefile
.PHONY: help install test build serve clean deploy lint format

# Default target
help:
	@echo "MyST Project - Make Commands"
	@echo ""
	@echo "Development:"
	@echo "  make install     Install all dependencies"
	@echo "  make test        Run test suite"
	@echo "  make lint        Run code quality checks"
	@echo "  make format      Auto-format code"
	@echo ""
	@echo "Book/Site:"
	@echo "  make build       Build MyST site"
	@echo "  make serve       Start development server (port 3001)"
	@echo "  make pdf         Generate PDF output"
	@echo "  make deploy      Deploy to GitHub Pages"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       Remove build artifacts"
	@echo "  make check-all   Run all checks"

# Install dependencies
install:
	pip install -e ".[dev,research]"
	npm install -g mystmd

# Run tests
test:
	pytest tests/ -v --cov=src --cov-report=term-missing

# Build MyST site
build:
	cd paper && myst build --html
	@echo "Site available at: paper/_build/html/index.html"

# Serve development server
serve:
	cd paper && myst start

# Generate PDF
pdf:
	cd paper && myst build --pdf

# Deploy to GitHub Pages
deploy:
	cd paper && myst build --gh-pages

# Clean build artifacts
clean:
	rm -rf paper/_build
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +

# Run all checks
check-all: lint test build
	@echo "All checks passed!"

# Lint code
lint:
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source
	black --check src tests

# Format code
format:
	black src tests
	isort src tests

.DEFAULT_GOAL := help
```

## Quick Setup Checklist

- [ ] Create `paper/` directory for MyST content
- [ ] Add `paper/myst.yml` configuration file
- [ ] Create `paper/.nojekyll` file
- [ ] Set up `pyproject.toml` with dependencies
- [ ] Create `.github/workflows/ci.yml` workflow
- [ ] Add proper `.gitignore` entries
- [ ] Configure GitHub repository settings → Pages → Source: GitHub Actions
- [ ] Test locally with `cd paper && myst start`
- [ ] Push to main branch to trigger deployment
- [ ] Verify site at `https://username.github.io/repository-name/`

## Troubleshooting

If deployment fails:

1. Check GitHub Actions logs for specific errors
2. Verify all required files are present and properly configured
3. Ensure `.nojekyll` file exists in both source and build output
4. Confirm GitHub Pages is configured to use GitHub Actions
5. Test build locally: `cd paper && myst build --html`

## Additional Resources

- [MyST Documentation](https://mystmd.org/)
- [MyST Templates](https://mystmd.org/guide/templates)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

This guide provides a complete, production-ready setup for deploying MyST content to GitHub Pages. Follow it step-by-step for reliable, automated deployments of your MyST-based documentation and books.
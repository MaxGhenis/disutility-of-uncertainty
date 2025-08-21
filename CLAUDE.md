# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains simulations exploring how uncertainty around marginal tax rates affects social welfare. It implements economic models using Cobb-Douglas utility functions to analyze the relationship between taxation, leisure, consumption, and welfare.

## Development Setup

The project uses Jupyter notebooks for simulation and analysis. The main notebook is `sim.ipynb`.

### Dependencies
- numpy
- plotly (for visualization)

To run the notebook:
```bash
jupyter notebook sim.ipynb
```

## Project Structure

The repository contains a single Jupyter notebook that implements:
- Cobb-Douglas utility functions for modeling agent preferences
- Optimal leisure calculations given wages, tax rates, and transfers  
- Visualizations showing income and substitution effects
- Planned extensions for multi-period models with agent heterogeneity and tax rate uncertainty

## Key Implementation Notes

The simulation uses the following economic model:
- Utility function: U = L^a * Y^b (Cobb-Douglas form)
- Optimal leisure formula: L = a(wT+v)/[w(a+b)]
- Where L=leisure, Y=income, w=wage, v=nonlabor income, T=total time available

The notebook explores how agents respond to different tax rates and transfer levels, with the income effect currently dominating the substitution effect in the implemented scenarios.
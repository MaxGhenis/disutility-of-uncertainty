# Data Appendix

## Primary Data Sources

### PolicyEngine-US
- Comprehensive tax calculator for U.S. households
- Incorporates federal and state tax codes
- Accounts for credits, deductions, and phase-outs
- Version 0.700.0 or higher required

### Current Population Survey (CPS)
- Annual Social and Economic Supplement (ASEC)
- Sample size: ~60,000 households
- Variables: Income, employment, demographics
- Years: 2019-2024

### IRS Statistics of Income (SOI)
- Administrative tax return data
- Aggregated to preserve confidentiality
- Marginal tax rate distributions by income
- Years: 2018-2022

## Variable Definitions

**Marginal Tax Rate (MTR)**: The tax rate on an additional dollar of income, including federal income tax, state income tax, and payroll taxes, accounting for all applicable credits and deductions.

**Wage Rate**: Hourly earnings calculated as annual labor income divided by annual hours worked (imputed as 2000 for full-time workers).

**Tax Rate Uncertainty**: Standard deviation of possible tax rates faced by a household, measured as either:
1. Historical variation in effective rates over past 5 years
2. Subjective uncertainty from survey responses
3. Complexity-based measure using tax form interactions

## Sample Construction

Starting with CPS microdata, we:
1. Select households with positive labor income
2. Exclude self-employed (different tax treatment)
3. Match to PolicyEngine-US for tax calculations
4. Compute marginal rates using \$1000 income increments
5. Weight observations using CPS household weights

Final sample: ~45,000 households representative of U.S. population

## Robustness Sample Definitions

Alternative samples used in robustness checks:
- Prime-age workers: Ages 25-54 only
- Full-time workers: 35+ hours per week
- Stable employment: Same job for 2+ years
- High-tax states: CA, NY, NJ, CT, MA
- Low-tax states: TX, FL, WA, NV, TN

## Code and Replication

All analysis code is available at: https://github.com/maxghenis/disutility-of-uncertainty

Requirements:
- Python 3.9+
- PolicyEngine-US
- NumPy, Pandas, SciPy
- Jupyter notebooks for exhibits

Replication instructions provided in repository README.

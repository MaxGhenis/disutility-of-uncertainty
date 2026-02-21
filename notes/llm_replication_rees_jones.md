# LLM replication of Rees-Jones & Taubinsky (2020)

## Idea

Replicate the survey instrument from Rees-Jones & Taubinsky (2020) using LLMs
(GPT-4, Claude, Gemini, etc.) to measure whether AI systems exhibit the same
"ironing" heuristic that human taxpayers use.

## Motivation

- R-J&T measured misperception of **federal income tax only**. Their survey asked
  respondents about federal marginal rates, not comprehensive rates (including
  payroll, state, or benefit phase-outs).
- The calibrated sigma = 0.12 from their cross-sectional RMSE is therefore a
  **lower bound** on comprehensive MTR misperception, since workers face
  additional sources of complexity beyond federal income tax.
- LLMs could serve as a benchmark: if AI systems with access to tax code
  knowledge still make systematic errors when asked to compute MTRs from
  realistic household scenarios, this would validate the structural misperception
  hypothesis.

## Design sketch

1. Construct ~100 household scenarios (income, filing status, state, dependents,
   deductions) spanning the income distribution.
2. For each scenario, compute the true comprehensive MTR using PolicyEngine-US.
3. Present each scenario to multiple LLMs and ask: "What is this household's
   marginal tax rate?"
4. Compare LLM responses to true MTRs. Compute RMSE, bias, and distributional
   patterns.
5. Vary prompt complexity (federal-only vs. comprehensive) to isolate the effect
   of tax system complexity on misperception.

## Expected findings

- LLMs will likely perform well on federal-only MTR questions (the training data
  includes abundant tax bracket information).
- Comprehensive MTR estimation (including EITC phase-outs, state taxes, payroll
  taxes, benefit cliffs) will likely show higher error rates, supporting the
  claim that sigma = 0.12 is a lower bound.
- The ironing heuristic (MTR ≈ ATR) may appear in LLM responses, especially for
  scenarios in phase-out ranges.

## Status

Future work. Not yet started.

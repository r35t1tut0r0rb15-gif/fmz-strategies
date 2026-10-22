# #474883 Multiple Moving Average and Stochastic Oscillator Crossover Quantitative Strategy -> `fmz_474883_ma10_over_ma5_ma6_stoch_cross_reversal`

- FMZ source id: 474883 (lineage).
- Source: https://www.fmz.com/strategy/474883 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 17:23:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stacked MA / stochastic crossings, as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths constants).

## Ambiguities resolved

- The sell test overlaps the buy (as written); the short wins ties. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`

# #476262 Adaptive Trading Strategy Based on Stochastic RSI Dual Line Crossover -> `fmz_476262_stoch_rsi14_kd_cross_band_reversal`

- FMZ source id: 476262 (lineage).
- Source: https://www.fmz.com/strategy/476262 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 15:06:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI crossings in the outer bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_period` [14, 21] x `lower_band` [20, 10]: **4 trials**; upper band 100 - lower.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`

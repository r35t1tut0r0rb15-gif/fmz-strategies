# #434436 Weighted Quantitative Moving Average Crossover Trading Strategy -> `fmz_434436_vwmacd_25_29_signal_cross_daily_reversal`

- FMZ source id: 434436 (lineage).
- Source: https://www.fmz.com/strategy/434436 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-06 12:05:01). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-weighted MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, commission 0.18 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [25, 12] x `slow_ma` [29, 26]: **4 trials**; signal 9.

## Ambiguities resolved

- Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_variant"`.

## Marks

`none`

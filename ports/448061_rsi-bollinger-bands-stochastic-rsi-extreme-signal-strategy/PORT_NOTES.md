# #448061 布林带随机RSI极值信号策略-Bollinger-Bands-Stochastic-RSI-Extreme-Signal-Strategy -> `fmz_448061_band_reentry_stochrsi_extreme_swapped_sides_reversal`

- FMZ source id: 448061 (lineage).
- Source: https://www.fmz.com/strategy/448061 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-12 16:36:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C178). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-entries after stochastic-RSI extremes (sides as sent) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `upper_limit` [90.0, 80.0]: **4 trials**; the lower limit and the stochastic-RSI lengths fixed.

## Ambiguities resolved

- Sides swapped as written (Bear -> long). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

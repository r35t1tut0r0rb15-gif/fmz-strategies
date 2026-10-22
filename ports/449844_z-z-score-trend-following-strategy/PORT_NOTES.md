# #449844 基于Z值的趋势跟踪策略-Z-Score-Trend-Following-Strategy -> `fmz_449844_zscore_ema100_threshold_cross_reversal`

- FMZ source id: 449844 (lineage).
- Source: https://www.fmz.com/strategy/449844 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 17:03:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Z-score threshold crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 10 % of equity size stored; commission and slippage are costs, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `threshold` [1.0, 1.5]: **4 trials**; one length for the EMA and the sd, as their defaults agree.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`

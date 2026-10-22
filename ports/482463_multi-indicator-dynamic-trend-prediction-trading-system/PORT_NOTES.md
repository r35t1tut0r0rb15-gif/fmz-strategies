# #482463 Multi Indicator Dynamic Trend Prediction Trading System -> `fmz_482463_rsi_stoch_extreme_prev_day_pivot_filter_mid_exit_reversal`

- FMZ source id: 482463 (lineage).
- Source: https://www.fmz.com/strategy/482463 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:22:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; previous broker day's pivots |
| 2 | PASS | RSI / Stochastic extremes with daily pivot filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `stoch_k` [14, 21]: **4 trials**; 70 / 30, 80 / 20, pivots 3 / 3 on broker days.

## Ambiguities resolved

- The daily pivot is na on most days (nz gives 0), as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`

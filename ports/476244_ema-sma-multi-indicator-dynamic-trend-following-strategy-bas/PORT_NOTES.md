# #476244 基于EMA和SMA的多重指标动态趋势跟踪策略-Multi-Indicator-Dynamic-Trend-Following-Strategy-Based-on-EMA-and-SMA -> `fmz_476244_sma_of_ema_cross_near_pivot_reversal`

- FMZ source id: 476244 (lineage).
- Source: https://www.fmz.com/strategy/476244 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 14:12:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C230). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed MA crossings near confirmed pivots |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`prd` [2, 4] x `window` [3, 5]: **4 trials**; the MA lengths fixed.

## Ambiguities resolved

- The "D" request is the daily chart's own data. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

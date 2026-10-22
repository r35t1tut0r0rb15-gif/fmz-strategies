# #482515 神经均线交叉趋势跟踪策略结合EMA过滤系统-Neural-Moving-Average-Crossover-Trend-Following-Strategy-with-EMA-Filtering-System -> `fmz_482515_ema200_side_after_sma9_15_cross_reentry_reversal`

- FMZ source id: 482515 (lineage).
- Source: https://www.fmz.com/strategy/482515 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 18:29:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C246). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA 200 side after SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [200, 100] x `sma_fast` [9, 5]: **4 trials**; SMA 15.

## Ambiguities resolved

- The same-bar close and re-entry is one continuous position here. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

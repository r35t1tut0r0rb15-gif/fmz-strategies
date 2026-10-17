# #488241 多均线交叉量化策略系统基于自适应移动平均线的趋势跟踪与交易信号优化-Adaptive-Moving-Average-Crossover-Quantitative-Strategy-Trend-Following-and-Trading-Signal-Optimization -> `fmz_488241_ma9_21_cross_long_only`

- FMZ source id: 488241 (lineage).
- Source: https://www.fmz.com/strategy/488241 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 11:09:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_type` ["SMA", "EMA"] x `slow` [21, 50]: **4 trials**; defaults SMA / 21 (the source's); fast 9 fixed. The VWMA
option uses volume (check 8) and is not offered; WMA is not in the grid.

## Ambiguities resolved

- Long only, exit on the opposite cross: opposite entries cannot occur. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

# #439708 双移动平均线交叉MACD趋势跟踪策略Dual-Moving-Average-Crossover-MACD-Trend-Following-Strategy -> `fmz_439708_macd_green_red_state_long`

- FMZ source id: 439708 (lineage).
- Source: https://www.fmz.com/strategy/439708 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 11:22:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [12, 8] x `slow_length` [26, 21]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`

# #458275 增强型EMA-WMA交叉策略与综合退出条件Enhanced-EMA-WMA-Crossover-Strategy-with-Comprehensive-Exit-Conditions -> `fmz_458275_ema9_wma30_cross_macd_close_count_exit_long_only`

- FMZ source id: 458275 (lineage).
- Source: https://www.fmz.com/strategy/458275 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:47:01). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA / WMA crossings confirmed by MACD with close-count and MACD exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 12] x `slow` [30, 40]: **4 trials**; MACD 12 / 26 / 9.

## Ambiguities resolved

- Closes act from the bar after the fill; counters reset after a close. Volume not used. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

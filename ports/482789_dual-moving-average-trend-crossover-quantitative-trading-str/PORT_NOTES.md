# #482789 双均线趋势交叉量化交易策略研究与优化-Dual-Moving-Average-Trend-Crossover-Quantitative-Trading-Strategy-Analysis-and-Optimization -> `fmz_482789_sma9_21_cross_long`

- FMZ source id: 482789 (lineage).
- Source: https://www.fmz.com/strategy/482789 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:48:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Two SMAs. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; defaults 9 / 21 (the source's).

## Ambiguities resolved

- The trade counters and label are statistics only. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none

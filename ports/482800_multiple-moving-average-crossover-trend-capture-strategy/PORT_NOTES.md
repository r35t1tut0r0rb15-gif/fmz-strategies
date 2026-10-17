# #482800 多重移动平均线交叉趋势捕捉策略-Multiple-Moving-Average-Crossover-Trend-Capture-Strategy -> `fmz_482800_sma1_2_cross_sma4_always_in`

- FMZ source id: 482800 (lineage).
- Source: https://www.fmz.com/strategy/482800 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 11:31:18). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Short SMAs. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`t_len` [2, 3] x `f_len` [4, 8]: **4 trials**; defaults 2 / 4 (the source's); SMA 1 (the close) fixed.

## Ambiguities resolved

- The closes repeat the reversal of the entries. REVERSAL INTENDED (always in). Daily bars: broker days stamped
  with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none

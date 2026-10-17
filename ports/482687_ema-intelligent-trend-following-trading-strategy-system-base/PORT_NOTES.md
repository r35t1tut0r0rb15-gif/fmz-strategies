# #482687 基于EMA双均线交叉的智能趋势跟踪交易策略系统-Intelligent-Trend-Following-Trading-Strategy-System-Based-on-EMA-Double-Moving-Average-Crossover -> `fmz_482687_ema10_20_cross_confirmed_window`

- FMZ source id: 482687 (lineage).
- Source: https://www.fmz.com/strategy/482687 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:52:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Two EMAs. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [20, 50]: **4 trials**; defaults 10 / 20 (the source's).

## Ambiguities resolved

- Clock rule (check 9 / C6): the 2017-01-01 00:00 to 2029-01-30 23:59 window, read as UTC; signals outside it are
  dropped, a held position stays open (as written).
- Same signals as #482764 (same batch) plus the window; not in a near-duplicate group, so ported (rule 7).
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none

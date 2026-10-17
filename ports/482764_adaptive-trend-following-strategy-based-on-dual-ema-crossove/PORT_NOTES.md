# #482764 基于双均线交叉的趋势跟踪自适应策略-Adaptive-Trend-Following-Strategy-Based-on-Dual-EMA-Crossover-System -> `fmz_482764_ema10_20_cross_confirmed_always_in`

- FMZ source id: 482764 (lineage).
- Source: https://www.fmz.com/strategy/482764 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:52:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
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

- REVERSAL INTENDED (always in). FREQ = "1h". #482687 (same batch) is the same script plus a 2017-2029 date window;
  not in a near-duplicate group, so both are ported (rule 7).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none

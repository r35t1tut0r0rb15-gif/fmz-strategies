# #455353 EMA-SMA多指标综合趋势跟踪策略-EMA-SMA-Multi-Indicator-Comprehensive-Trend-Following-Strategy -> `fmz_455353_seventeen_indicator_vote_threshold_reversal`

- FMZ source id: 455353 (lineage).
- Source: https://www.fmz.com/strategy/455353 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-28 15:00:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Multi-indicator vote thresholds |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_lvl` [12, 10, 14] x `close_lvl` [9, 5]: **6 trials**; the indicator lengths fixed.

## Ambiguities resolved

- Closes before entries. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

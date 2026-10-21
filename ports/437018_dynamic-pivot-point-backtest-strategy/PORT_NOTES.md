# #437018 Dynamic Pivot Point Backtest Strategy -> `fmz_437018_daily_pivot_r1_s1_state`

- FMZ source id: 437018 (lineage).
- Source: https://www.fmz.com/strategy/437018 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-29 15:50:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C98). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from the completed day |
| 2 | PASS | Pivot levels from the previous day |
| 3 | PASS | No exchange named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True]: **2 trials** (the script's only input).

## Ambiguities resolved

- No bar size (bar_size_pending); previous broker day's pivots. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`bar_size_pending`

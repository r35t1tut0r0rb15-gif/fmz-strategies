# #438051 Breakthrough Highs and Lows Backtesting Strategy -> `fmz_438051_previous_day_level_state`

- FMZ source id: 438051 (lineage).
- Source: https://www.fmz.com/strategy/438051 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-08 16:13:44). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Previous-day levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [1, 2, 3, 5]: **4 trials**; reverse off.

## Ambiguities resolved

- Swapped level labels as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`

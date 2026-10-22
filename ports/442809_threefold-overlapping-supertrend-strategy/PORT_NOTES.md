# #442809 Threefold Overlapping SuperTrend Strategy -> `fmz_442809_triple_supertrend_cross_one_bar_hold`

- FMZ source id: 442809 (lineage).
- Source: https://www.fmz.com/strategy/442809 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 10:04:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Triple SuperTrend agreement; one-bar holds as written |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor1` [3.0, 2.0] x `atr1` [10, 20]: **4 trials**; the second and third SuperTrends fixed.

## Ambiguities resolved

- close_all every bar (one-bar holds), as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

# #435960 趋势追踪-turtle系统Turtle-Trend-Trading-System -> `fmz_435960_turtle_55_20_channel`

- FMZ source id: 435960 (lineage).
- Source: https://www.fmz.com/strategy/435960 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 14:16:48). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`n` [55, 40] x `e` [20, 10]: **4 trials**.

## Ambiguities resolved

- Previous bar's channel; orders in call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`

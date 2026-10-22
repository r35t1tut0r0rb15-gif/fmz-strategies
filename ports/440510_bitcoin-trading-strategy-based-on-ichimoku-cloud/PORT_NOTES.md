# #440510 Bitcoin Trading Strategy Based on Ichimoku Cloud -> `fmz_440510_range_midline_cross_long`

- FMZ source id: 440510 (lineage).
- Source: https://www.fmz.com/strategy/440510 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-31 11:06:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C136). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Range mid-point lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_max` [20, 52] x `period_min` [16, 26]: **4 trials**; the middle period 10 fixed.

## Ambiguities resolved

- Date window dropped. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

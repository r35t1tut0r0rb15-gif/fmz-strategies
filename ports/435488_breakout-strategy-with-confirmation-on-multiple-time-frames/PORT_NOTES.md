# #435488 Breakout Strategy with Confirmation on Multiple Time Frames -> `fmz_435488_daily_open_370_cross_patterns`

- FMZ source id: 435488 (lineage).
- Source: https://www.fmz.com/strategy/435488 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-15 12:16:55). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; higher-timeframe values from completed bars |
| 2 | REVIEW | Patterns act only before the first trade; reversals on crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pct_p` [66, 75] x `sim` [370, 240]: **4 trials**; the other pattern settings fixed.

## Ambiguities resolved

- Higher bars built from minutes; patterns only before the first trade. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

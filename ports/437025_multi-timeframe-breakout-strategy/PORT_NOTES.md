# #437025 Multi Timeframe Breakout Strategy -> `fmz_437025_noro_week_day_levels`

- FMZ source id: 437025 (lineage).
- Source: https://www.fmz.com/strategy/437025 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-29 16:18:22). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C98). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; higher-timeframe values from completed periods |
| 2 | PASS | Levels from the instrument's own completed periods |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based lot and capital % stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`saw_filter` [True, False] x `color_filter` [True, False]: **4 trials**; W and D levels of ohlc4 fixed.

## Ambiguities resolved

- Higher timeframes as the last completed broker day / week; date window dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`

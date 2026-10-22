# #468331 Multi Indicator Dynamic Stop Loss Trend Following Strategy -> `fmz_468331_ut_bot_trail_cross_hull31_slope_reversal`

- FMZ source id: 468331 (lineage).
- Source: https://www.fmz.com/strategy/468331 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 16:03:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR-trail crossings with a Hull slope filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [2.0, 1.0] x `atr_len` [1, 10] x `hull_len` [31, 55]: **8 trials**.

## Ambiguities resolved

- Heikin Ashi source off (default). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`

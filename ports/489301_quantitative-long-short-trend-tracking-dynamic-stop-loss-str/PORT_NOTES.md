# #489301 Quantitative Long Short Trend Tracking Dynamic Stop Loss Strategy -> `fmz_489301_ut_atr10_trail_line_cross_long`

- FMZ source id: 489301 (lineage).
- Source: https://www.fmz.com/strategy/489301 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:34:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing-line crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a` [1.0, 2.0] x `c` [10, 20]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`

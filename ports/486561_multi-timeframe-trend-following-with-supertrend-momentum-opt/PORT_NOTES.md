# #486561 Multi Timeframe Trend Following with Supertrend Momentum Optimization Strategy -> `fmz_486561_supertrend3_10_turn_ema200_side_line_stop_2r_reversal`

- FMZ source id: 486561 (lineage).
- Source: https://www.fmz.com/strategy/486561 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-14 09:17:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C263). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; SuperTrend stop and 2R target as fractions of the fill |
| 2 | PASS | SuperTrend turns on the EMA 200 side |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_period` [10, 14]: **4 trials**; EMA 200, target 2R.

## Ambiguities resolved

- A same-side re-entry's new levels are pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`

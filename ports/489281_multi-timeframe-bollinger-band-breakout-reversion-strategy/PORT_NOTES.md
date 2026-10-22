# #489281 Multi Timeframe Bollinger Band Breakout Reversion Strategy -> `fmz_489281_bb20_15_outside_candle_break_3r_close_target_reversal`

- FMZ source id: 489281 (lineage).
- Source: https://www.fmz.com/strategy/489281 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 10:26:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C270). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested 3 R target; the armed break-even stop pending |
| 2 | PASS | Outside-band candle breaks with an R-multiple target |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity (4000 / risk) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.5, 2.0] x `rr` [3.0, 2.0]: **4 trials**; BB 20, break window 4.

## Ambiguities resolved

- The armed break-even stop is pending; the shared levels are followed in a loop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`

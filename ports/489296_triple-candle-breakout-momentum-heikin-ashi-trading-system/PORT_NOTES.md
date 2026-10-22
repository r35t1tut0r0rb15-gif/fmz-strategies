# #489296 Triple Candle Breakout Momentum Heikin Ashi Trading System -> `fmz_489296_heikin_ashi_3streak_breakout_candle_exit_reversal`

- FMZ source id: 489296 (lineage).
- Source: https://www.fmz.com/strategy/489296 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-03 11:17:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C271). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Heikin-Ashi streak breakouts with candle-low exits |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`streak` [3, 2, 4]: **3 trials**.

## Ambiguities resolved

- The level / flag loop is as written. REVERSAL INTENDED. FREQ = "1D" (broker days). MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi"`.

## Marks

`none`

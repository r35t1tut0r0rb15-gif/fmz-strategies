# #488244 Cross Breakout Dual EMA System Strategy -> `fmz_488244_ema32_hl_band_cross_clear_candle_breakout_reversal`

- FMZ source id: 488244 (lineage).
- Source: https://www.fmz.com/strategy/488244 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 11:14:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA-band crossings with a first-clear-candle breakout |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [32, 20, 50]: **3 trials**.

## Ambiguities resolved

- The flag / level / valuewhen loop is as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_breakout"`.

## Marks

`none`

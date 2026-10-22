# #474050 Multi Indicator Crossover Momentum Trend Following Strategy with Optimized Take Profit and Stop Loss System -> `fmz_474050_alligator_lips_teeth_cross_ao_ac_swing_bracket_reversal`

- FMZ source id: 474050 (lineage).
- Source: https://www.fmz.com/strategy/474050 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 16:21:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Alligator crossings with AO / AC filters and a swing bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lips_len` [5, 3] x `teeth_len` [8, 13]: **4 trials**; the offsets 3 / 5.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`

# #439608 Bollinger Bands Channel Breakout Mean Reversion Strategy -> `fmz_439608_lower_band_reclaim_low_stop_long`

- FMZ source id: 439608 (lineage).
- Source: https://www.fmz.com/strategy/439608 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 10:47:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving target pending |
| 2 | PASS | Bollinger crossings and the signal-bar low |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Upper-band target pending; stop from the signal-bar low. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

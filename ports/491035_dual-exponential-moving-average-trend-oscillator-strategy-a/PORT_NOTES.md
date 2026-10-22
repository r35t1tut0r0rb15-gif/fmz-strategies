# #491035 Dual Exponential Moving Average Trend Oscillator Strategy A Standard Deviation Based Dynamic Quantitative Trading Model -> `fmz_491035_dema40_norm_band_breakout_band_stop_15r_reversal`

- FMZ source id: 491035 (lineage).
- Source: https://www.fmz.com/strategy/491035 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-18 09:19:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; band bracket as fractions of the fill; the trail pending |
| 2 | PASS | Normalised DEMA band breakouts |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_dema` [40, 20] x `RR` [1.5, 3.0]: **4 trials**; base 20, thresholds 55 / 45.

## Ambiguities resolved

- The fixed-ATR trail is pending. REVERSAL INTENDED. FREQ = "1h". MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "band_breakout"`.

## Marks

`trailing_stop_pending`

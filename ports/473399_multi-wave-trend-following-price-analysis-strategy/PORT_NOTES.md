# #473399 Multi Wave Trend Following Price Analysis Strategy -> `fmz_473399_three_higher_lows_lower_highs_point_bracket_reversal`

- FMZ source id: 473399 (lineage).
- Source: https://www.fmz.com/strategy/473399 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:40:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C218). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the price bracket as fractions of the signal close |
| 2 | PASS | Staircase counts with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The price bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.0000476, 0.00476] x `tp_frac` [0.000143, 0.0143]: **4 trials**.

## Ambiguities resolved

- Price amounts as fractions of 42000. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`

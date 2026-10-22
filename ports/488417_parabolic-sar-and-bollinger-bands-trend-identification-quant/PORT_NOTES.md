# #488417 Parabolic SAR and Bollinger Bands Trend Identification Quantitative Trading Strategy -> `fmz_488417_psar_side_inside_bb20_2_reversal`

- FMZ source id: 488417 (lineage).
- Source: https://www.fmz.com/strategy/488417 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-27 14:20:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C266). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Parabolic SAR side within the Bollinger bands |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sar_max` [0.2, 0.1] x `bb_mult` [2.0, 2.5]: **4 trials**; SAR start 0.02, BB 20.

## Ambiguities resolved

- The SAR increment equals its maximum, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`

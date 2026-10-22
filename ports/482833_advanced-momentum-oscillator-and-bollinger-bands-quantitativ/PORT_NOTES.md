# #482833 Advanced Momentum Oscillator and Bollinger Bands Quantitative Strategy System -> `fmz_482833_bb20_2_cross_cmo14_50_basis_exit_reversal`

- FMZ source id: 482833 (lineage).
- Source: https://www.fmz.com/strategy/482833 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:50:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band crossings with CMO extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 40] x `cmo_length` [14, 9]: **4 trials**; band 2.0 sd, CMO levels 50 / -50.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

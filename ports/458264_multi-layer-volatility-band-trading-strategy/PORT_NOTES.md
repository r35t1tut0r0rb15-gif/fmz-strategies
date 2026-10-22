# #458264 Multi Layer Volatility Band Trading Strategy -> `fmz_458264_layered_tr_band_fades_rearm_at_basis_reversal`

- FMZ source id: 458264 (lineage).
- Source: https://www.fmz.com/strategy/458264 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:08:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Layered volatility-band fades |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1-share quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`col_int` [12, 30] x `atr_bias` [0.72, 1.0]: **4 trials**; the layer factors fixed.

## Ambiguities resolved

- Default switches (collective value, dynamic multiplier, no basis exit). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`

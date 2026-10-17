# #433069 Combo Momentum Reversal Dual Rail Matching Strategy -> `fmz_433069_combo_123_ergodic_csi`

- FMZ source id: 433069 (lineage).
- Source: https://www.fmz.com/strategy/433069 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 10:17:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and a range / close ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `buy_zone` [0.02, 0.04]: **4 trials**; the 123 smoothing / level and the CSI settings fixed.

## Ambiguities resolved

- Overlapping CSI zones as written (above the buy zone = up, else down). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`

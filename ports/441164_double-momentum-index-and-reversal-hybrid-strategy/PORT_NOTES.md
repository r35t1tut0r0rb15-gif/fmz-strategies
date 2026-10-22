# #441164 Double Momentum Index and Reversal Hybrid Strategy -> `fmz_441164_reversal123_csi_combo`

- FMZ source id: 441164 (lineage).
- Source: https://www.fmz.com/strategy/441164 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-06 12:22:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C148). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close pattern, stochastic and CSI states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the CSI's point value, margin and commission are only its constant). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `length_csi` [14, 28]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`

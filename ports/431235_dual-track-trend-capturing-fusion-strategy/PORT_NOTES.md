# #431235 Dual track Trend Capturing Fusion Strategy -> `fmz_431235_combo_123_smi_ergodic`

- FMZ source id: 431235 (lineage).
- Source: https://www.fmz.com/strategy/431235 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-06 11:49:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A stochastic and a true-strength ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `band` [0.5, 0.25]: **4 trials**; K 1, D 3, level 50 and SMI 4 / 8 / 3 fixed; LowBand = -band.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`

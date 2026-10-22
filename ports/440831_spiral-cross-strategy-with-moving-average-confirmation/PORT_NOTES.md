# #440831 Spiral Cross Strategy with Moving Average Confirmation -> `fmz_440831_vortex_cross_smoothed_sma_filter`

- FMZ source id: 440831 (lineage).
- Source: https://www.fmz.com/strategy/440831 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 14:50:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Vortex crossings and a smoothed SMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 21] x `ma_len` [9, 20]: **4 trials**; smoothing 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`

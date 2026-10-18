# #436102 Dual Moving Average Trend Tracking Strategy -> `fmz_436102_zero_lag_ema_rma_state`

- FMZ source id: 436102 (lineage).
- Source: https://www.fmz.com/strategy/436102 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-21 11:45:35). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Zero-lag averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity-based lot, capital percent and pyramiding inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [14, 21] x `len2` [14, 21]: **4 trials**.

## Ambiguities resolved

- Previous bar's states; unused series dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

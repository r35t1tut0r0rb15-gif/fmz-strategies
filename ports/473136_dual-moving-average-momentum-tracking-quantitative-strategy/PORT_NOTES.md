# #473136 Dual Moving Average Momentum Tracking Quantitative Strategy -> `fmz_473136_close_cross_smoothed_sma9_reversal`

- FMZ source id: 473136 (lineage).
- Source: https://www.fmz.com/strategy/473136 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 15:06:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close crossings of a double-smoothed average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [9, 20] x `smoothing` [5, 10]: **4 trials**.

## Ambiguities resolved

- SMA smoothing (default). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

# #482771 Quantum Spectral Momentum Trading Strategy with Multi Component Analysis -> `fmz_482771_composite_zscore_ema_ratio_index_70_30_reversal`

- FMZ source id: 482771 (lineage).
- Source: https://www.fmz.com/strategy/482771 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; re-sent bar stops described (pending) |
| 2 | PASS | Composite z-score / momentum index thresholds |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [50, 100] x `entry_band` [20.0, 10.0]: **4 trials**; entries at 50 +/- band; EMA 20 / 50, weights 20 / 30 / 20 / 10.

## Ambiguities resolved

- The bar stops are pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_momentum"`.

## Marks

`trailing_stop_pending`

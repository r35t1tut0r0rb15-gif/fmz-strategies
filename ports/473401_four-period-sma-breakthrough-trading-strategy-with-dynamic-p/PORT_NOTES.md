# #473401 Four Period SMA Breakthrough Trading Strategy with Dynamic Profit Loss Management System -> `fmz_473401_close_cross_sma4_avg_bracket_reversal`

- FMZ source id: 473401 (lineage).
- Source: https://www.fmz.com/strategy/473401 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:44:42). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C218). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the average-price bracket as fixed fractions |
| 2 | PASS | SMA 4 crossings with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [4, 10] x `tp_pct` [0.02, 0.04] x `sl_pct` [0.01, 0.02]: **8 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

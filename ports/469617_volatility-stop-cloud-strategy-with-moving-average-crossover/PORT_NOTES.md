# #469617 Volatility Stop Cloud Strategy with Moving Average Crossover System -> `fmz_469617_small_vs_big_volatility_stop_cross_reversal`

- FMZ source id: 469617 (lineage).
- Source: https://www.fmz.com/strategy/469617 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-10-14 11:42:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C208). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility-stop crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 14] x `factor_small` [1.5, 1.0] x `factor_big` [3.0, 4.0]: **8 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`

# #434695 Binomial Moving Average Trend Strategy -> `fmz_434695_binomial_ma_cross`

- FMZ source id: 434695 (lineage).
- Source: https://www.fmz.com/strategy/434695 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-08 14:55:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Weighted average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() margins stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [30, 20]: **4 trials**.

## Ambiguities resolved

- Exact binomial coefficients (the factorial overflow for n = 30 not reproduced). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

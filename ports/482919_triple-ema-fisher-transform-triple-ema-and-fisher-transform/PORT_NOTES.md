# #482919 Triple-EMA和Fisher-Transform趋势动量策略-Triple-EMA-and-Fisher-Transform-Trend-Momentum-Strategy -> `fmz_482919_tema21_fisher10_zero_cross_reversal`

- FMZ source id: 482919 (lineage).
- Source: https://www.fmz.com/strategy/482919 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 17:41:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C253). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TEMA crossings with Fisher zero crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tema_length` [21, 10] x `fisher_length` [10, 20]: **4 trials**; smoothing 1.

## Ambiguities resolved

- Fisher as written (no recursive value smoothing); a flat range gives na, read as 0 next bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

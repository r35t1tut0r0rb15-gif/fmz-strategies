# #482474 Gamma Weighted Momentum Based Bitcoin Futures Intelligent Trading Strategy -> `fmz_482474_gamma075_weighted_avg60_close_side_3bar_momentum_reversal`

- FMZ source id: 482474 (lineage).
- Source: https://www.fmz.com/strategy/482474 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:45:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Weighted-average side with a close momentum filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash 50000 stored, not ported; slippage and commission not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [60, 30] x `gamma_factor` [0.75, 0.9]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

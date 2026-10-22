# #452742 混合双态Z评分量化策略-Hybrid-Binomial-Z-Score-Quantitative-Strategy -> `fmz_452742_change_zscore_bollinger_extreme_long`

- FMZ source id: 452742 (lineage).
- Source: https://www.fmz.com/strategy/452742 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 17:38:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Extreme-change dips below the band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [20, 50] x `z_thr` [1.5, 2.0] x `lookback` [252, 126]: **8 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

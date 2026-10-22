# #452359 CCI双均线交叉回撤买入策略-CCI-MA-Crossover-Pullback-Buy-Strategy -> `fmz_452359_ema10_30_pullback_cci_extreme_reversal`

- FMZ source id: 452359 (lineage).
- Source: https://www.fmz.com/strategy/452359 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-24 17:45:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend pullbacks with CCI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [30, 50] x `cci_len` [20, 14]: **8 trials**; the threshold 100 fixed.

## Ambiguities resolved

- One-bar-lagged averages as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`

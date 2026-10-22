# #453244 RSI与线性回归通道交易策略-RSI-and-Linear-Regression-Channel-Trading-Strategy -> `fmz_453244_linreg_channel_rsi_extreme_long`

- FMZ source id: 453244 (lineage).
- Source: https://www.fmz.com/strategy/453244 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 11:19:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C191). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression-channel extremes with RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel_len` [100, 50] x `rsi_len` [14, 7]: **4 trials**; the levels fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

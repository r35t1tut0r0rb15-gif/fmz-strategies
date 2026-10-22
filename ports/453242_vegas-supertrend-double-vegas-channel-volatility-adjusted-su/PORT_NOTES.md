# #453242 双重Vegas通道波动性调整SuperTrend量化交易策略-Double-Vegas-Channel-Volatility-Adjusted-SuperTrend-Quantitative-Trading-Strategy -> `fmz_453242_double_vegas_supertrend_hold_days_reversal`

- FMZ source id: 453242 (lineage).
- Source: https://www.fmz.com/strategy/453242 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 11:16:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C191). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Aligned volatility-adjusted SuperTrends with a time exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing, commission and slippage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult1` [5.0, 3.0] x `mult2` [7.0, 5.0] x `hold_days` [5, 10]: **8 trials**; the ATR and channel lengths fixed.

## Ambiguities resolved

- Hold counts from the last aligned bar. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

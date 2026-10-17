# #488023 长期趋势与波动率识别相结合的指数移动均线超级趋势量化交易策略-Long-term-Trend-and-Volatility-Recognition-Combined-Exponential-Moving-Average-SuperTrend-Quantitative-Trading-Strategy -> `fmz_488023_sma200_classic_supertrend`

- FMZ source id: 488023 (lineage).
- Source: https://www.fmz.com/strategy/488023 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 14:42:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A moving average and an ATR band. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `ma_length` [200, 100]: **4 trials**; defaults 3 / 200 (the source's); ATR 14 fixed.

## Ambiguities resolved

- The SuperTrend recursion as written (na history compares false; the first trend is 1). The closes test the
  position at the bar's start (#430850). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

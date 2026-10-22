# #481352 双均线交叉与随机RSI超买超卖区间优化交易策略-Dual-Moving-Average-Crossover-with-Stochastic-RSI-Overbought-Oversold-Enhanced-Trading-Strategy -> `fmz_481352_stochrsi_cross_under20_sma21_55_trend_long`

- FMZ source id: 481352 (lineage).
- Source: https://www.fmz.com/strategy/481352 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-10 14:40:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C242). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI crossings in an SMA up-trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_len` [14, 21] x `fast_sma` [21, 50]: **4 trials**; slow SMA 55, K 3, D 3, 20 / 80.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`

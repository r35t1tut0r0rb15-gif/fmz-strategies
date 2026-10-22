# #439734 聚合多时间帧MACD-RSI-CCI-StochRSI-MA线性交易策略Aggregated-Multi-timeframe-MACD-RSI-CCI-StochRSI-MA-Linear-Trading-Strategy -> `fmz_439734_macd_cross_rsi_cci_stoch_sma200`

- FMZ source id: 439734 (lineage).
- Source: https://www.fmz.com/strategy/439734 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 14:11:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings and oscillator filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG439734. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_level` [70, 60] x `ma_len` [200, 100]: **4 trials**; MACD 12 / 26 / 9, CCI 14 level 100 and stochastic 14 / 3 fixed.

## Ambiguities resolved

- CCI short test cci > 0, as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

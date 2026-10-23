# #474952 基于RSIMACD和成交量的多指标组合自适应交易策略-Multi-Indicator-Adaptive-Trading-Strategy-Based-on-RSI-MACD-and-Volume -> `fmz_474952_macd_engulf_rsi_cum_net_volume_1h_long_only`

- FMZ source id: 474952 (lineage).
- Source: https://www.fmz.com/strategy/474952 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 10:19:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings / engulfing candles filtered by RSI and net volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_exit` [60.0, 70.0] x `sig_len` [9, 14]: **4 trials**; RSI 14, MACD 12 / 26.

## Ambiguities resolved

- Net volume cumulative from the data start. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`

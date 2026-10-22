# #478701 多重指标趋势跟踪结合RSI超买超卖的量化交易策略-Multi-Indicator-Trend-Following-with-RSI-Overbought-Oversold-Quantitative-Trading-Strategy -> `fmz_478701_macd_turn_below_zero_ema50_200_rsi70_exit_long`

- FMZ source id: 478701 (lineage).
- Source: https://www.fmz.com/strategy/478701 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 14:52:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C239). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD turns below zero in an EMA up-trend with RSI and trend exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_short` [50, 20] x `rsi_exit` [70, 60]: **4 trials**; EMA 200, MACD 12 / 26 / 9, RSI 14.

## Ambiguities resolved

- Long only. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`none`

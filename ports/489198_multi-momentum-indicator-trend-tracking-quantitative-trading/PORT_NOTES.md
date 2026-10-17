# #489198 多重动量指标趋势追踪量化交易策略-Multi-Momentum-Indicator-Trend-Tracking-Quantitative-Trading-Strategy -> `fmz_489198_ema_9_21_cross_rsi_macd_reverse`

- FMZ source id: 489198 (lineage).
- Source: https://www.fmz.com/strategy/489198 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 16:19:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMAs, RSI and MACD |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [9, 5] x `ema_slow` [21, 50]: **4 trials**; defaults 9 / 21 (the source's); RSI 14 and MACD 12 / 26 / 9
fixed.

## Ambiguities resolved

- The bearish signal closes the long and goes short (stop-and-reverse); the RSI 70 / 30 inputs are unused.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

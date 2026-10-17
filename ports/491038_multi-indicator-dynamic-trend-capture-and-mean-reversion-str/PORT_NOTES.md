# #491038 多指标动态趋势捕捉与均值回归策略-Multi-Indicator-Dynamic-Trend-Capture-and-Mean-Reversion-Strategy -> `fmz_491038_phoenix_ema_sma_rsi_always_in`

- FMZ source id: 491038 (lineage).
- Source: https://www.fmz.com/strategy/491038 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-18 09:27:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving averages and an oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [9, 5] x `sma_short` [20, 50]: **4 trials**; defaults 9 / 20 (the source's); EMA 21, RSI 14 (60 / 40)
and the Bollinger basis SMA 20 fixed.

## Ambiguities resolved

- Pivots, SMA 50, the bands and the (never-updating) zigzag are drawn only.
- The closes coincide with the opposite entries: a stop-and-reverse. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

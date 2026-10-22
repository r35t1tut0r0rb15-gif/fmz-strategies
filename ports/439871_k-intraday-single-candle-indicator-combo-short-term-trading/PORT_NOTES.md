# #439871 单根K线技术指标组合短期贸易策略Intraday-Single-Candle-Indicator-Combo-Short-Term-Trading-Strategy -> `fmz_439871_banknifty_mtf_macd_downtick_short`

- FMZ source id: 439871 (lineage).
- Source: https://www.fmz.com/strategy/439871 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-24 15:04:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; lower-time-frame values from the day's last bar |
| 2 | PASS | MACD slopes, RSI, ADX, stochastic and Bollinger filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_weak` [40, 50] x `adx_min` [12, 20]: **4 trials**; the MACD, stochastic and Bollinger settings fixed.

## Ambiguities resolved

- Lower-time-frame MACDs from the day's last bar; the square-off long reverses, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

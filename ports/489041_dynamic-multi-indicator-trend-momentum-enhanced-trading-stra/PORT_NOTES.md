# #489041 动态多指标趋势动量优化交易策略-Dynamic-Multi-Indicator-Trend-Momentum-Enhanced-Trading-Strategy -> `fmz_489041_ema_cross_trend_rsi_macd_atr_bracket_long`

- FMZ source id: 489041 (lineage).
- Source: https://www.fmz.com/strategy/489041 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-01 14:41:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | EMAs, oscillators and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 3.0] x `rr` [2.0, 1.0]: **4 trials**; defaults 1.5 / 2 (the source's); EMA 20 / 50 / 200, RSI 14
(55) and MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- The sell condition is computed but never traded: long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

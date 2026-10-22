# #482472 多指标动量突破结合平滑K线交易策略-Multi-Indicator-Momentum-Breakout-with-Smoothed-Candlestick-Trading-Strategy -> `fmz_482472_bb20_upper_break_ha_green_rsi50_ha_red_exit_long`

- FMZ source id: 482472 (lineage).
- Source: https://www.fmz.com/strategy/482472 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:38:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band breakouts with Heikin-Ashi colour and RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `bb_mult` [2.0, 1.5]: **4 trials**; RSI 14, 70.

## Ambiguities resolved

- Long only. FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`

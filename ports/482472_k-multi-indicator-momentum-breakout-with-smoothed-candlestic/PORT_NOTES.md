# #482472 多指标动量突破结合平滑K线交易策略-Multi-Indicator-Momentum-Breakout-with-Smoothed-Candlestick-Trading-Strategy -> `fmz_482472_ha_green_bb_upper_break_rsi_long`

- FMZ source id: 482472 (lineage).
- Source: https://www.fmz.com/strategy/482472 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:38:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Heikin-Ashi colour, Bollinger bands and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 1.5] x `rsi_exit` [70, 80]: **4 trials**; defaults 2 / 70 (the source's); BB 20 and RSI 14 fixed.

## Ambiguities resolved

- Heikin-Ashi open seeded with (open + close) / 2 on the first bar, as written.
- The close acts on the position held at the bar's start and never undoes an entry on that bar (#430850).
- Long only. FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

none

# #483791 高级趋势捕捉型均线交叉多指标确认交易策略-Advanced-Trend-Capturing-EMA-Crossover-Multi-Indicator-Confirmation-Trading-Strategy -> `fmz_483791_ema9_21_cross_filters_atr_bracket`

- FMZ source id: 483791 (lineage).
- Source: https://www.fmz.com/strategy/483791 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:36:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, RSI, the band middle and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.0, 1.5] x `tp_mult` [2.0, 3.0]: **4 trials**; defaults 1 / 2 (the source's); EMA 9 / 21, SMA 200, RSI 14,
BB 20 middle and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "10min" ("BTC/USD" is a label).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

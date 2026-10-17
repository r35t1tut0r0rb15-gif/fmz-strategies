# #483029 多重指标趋势跟踪动量交易策略-Multi-Indicator-Trend-Following-Momentum-Trading-Strategy -> `fmz_483029_macd_cross_pullback_trend_wide_bracket`

- FMZ source id: 483029 (lineage).
- Source: https://www.fmz.com/strategy/483029 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:06:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, RSI, MACD and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 2 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 20] x `pullback_bars` [5, 10]: **4 trials**; defaults 50 / 5 (the source's); SMA 200, RSI 14, MACD
12 / 26 / 9 and RR 1.5 fixed.

## Bracket as written

`limit = close x (1 + 1.5)` and `stop = close x (1 - 1 / 2.5)`: a +150 % target and a -40 % stop (shorts mirrored),
kept as written (fractions of the fill). `trail_price` without `trail_offset` places no trail: inert.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the bracket from the new close. The port keeps the entry's bracket.

## Ambiguities resolved

- `barssince` of a condition that never held is na: no signal. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {}
  (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`trailing_stop_pending`

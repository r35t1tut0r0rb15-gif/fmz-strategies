# #486561 多时间框架趋势跟踪与超级趋势动量优化策略-Multi-Timeframe-Trend-Following-with-Supertrend-Momentum-Optimization-Strategy -> `fmz_486561_ema200_supertrend_edge_bracket`

- FMZ source id: 486561 (lineage).
- Source: https://www.fmz.com/strategy/486561 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-14 09:17:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | An EMA and SuperTrend. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_period` [10, 14]: **4 trials**; defaults 3 / 10 (the source's); EMA 200 and the 2 R target
fixed.

## Trailing stop (mark `trailing_stop_pending`)

A new same-side signal edge while held runs `close_all` and re-enters, placing a new stop / target from the new bar.
The port keeps the entry's bracket (the SuperTrend line at the signal bar, re-based on the fill).

## Ambiguities resolved

- `request.security(syminfo.tickerid, "60", ...)` on the 1-hour chart is the bar's own value (house rule); "15M" in
  the title is a label. `close_all` + entry is the reversal: REVERSAL INTENDED. Stop module: `portfolio_kwargs` {}
  (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`

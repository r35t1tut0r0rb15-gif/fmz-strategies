# #484921 多重指标趋势确认动态止盈止损交易策略-Multi-Indicator-Trend-Confirmation-Dynamic-Risk-Management-Trading-Strategy -> `fmz_484921_close_cross_supertrend_bracket`

- FMZ source id: 484921 (lineage).
- Source: https://www.fmz.com/strategy/484921 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-05 10:19:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | SuperTrend, EMA, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_mult` [1.5, 2.5]: **4 trials**; defaults 3 / 1.5 (the source's); ATR 10, EMA 200, RSI 14
(filter on) and the 2 x target fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The SuperTrend line as `ta.supertrend` computes it. REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "3h": `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

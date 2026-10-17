# #482428 动态跟踪止损的三分之一K线量化交易策略-Dynamic-Third-Bar-Analysis-Strategy-with-Adaptive-Trailing-Stop -> `fmz_482428_trinity_bar_thirds_prev_bar_stop`

- FMZ source id: 482428 (lineage).
- Source: https://www.fmz.com/strategy/482428 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 13:57:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the previous-bar stop as exit signals (marked). |
| 2 | PASS | Thirds of each bar's range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 250 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | `ND482242` with #482242 (Jaccard 0.770, similar, not a duplicate). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_bars` [1, 2]: **2 trials**; default 1 (the source's). The bar-thirds pattern has no parameter.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit(stop = low[1])` (short: `high[1]`) is re-placed every bar while held, so the stop follows the previous
bar. The house bracket is fixed at the fill and cannot carry it. `simulate()` keeps the resting order (placed at a
bar's close, active from the next bar) and emits an exit signal on the bar whose low (high) reaches it, filled at the
next open (one bar after Pine's stop fill).

## Ambiguities resolved

- A zero-range bar meets both patterns: neither is taken. The trailing timeframe input is the chart's own.
- REVERSAL INTENDED. Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`trailing_stop_pending`

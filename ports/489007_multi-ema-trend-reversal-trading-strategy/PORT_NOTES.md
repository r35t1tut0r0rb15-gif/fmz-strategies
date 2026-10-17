# #489007 多重指数移动平均线趋势反转交易策略-Multi-EMA-Trend-Reversal-Trading-Strategy -> `fmz_489007_ema_perfect_order_start_end`

- FMZ source id: 489007 (lineage).
- Source: https://www.fmz.com/strategy/489007 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 10:02:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMAs only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`a` [10, 5] x `c` [30, 50]: **4 trials**; defaults 10 / 30 (the source's); EMA B 20 fixed.

## Ambiguities resolved

- The if / else-if chain as written: an opposite stack on the bar the old one breaks is an entry (reversal); the
  close_all runs once per end in its own branch.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

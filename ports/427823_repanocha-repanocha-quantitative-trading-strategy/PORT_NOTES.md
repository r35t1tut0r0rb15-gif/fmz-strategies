# #427823 RePaNoCHa Quantitative Trading Strategy -> `fmz_427823_repanocha_v4`

- FMZ source id: 427823 (lineage).
- Source: https://www.fmz.com/strategy/427823 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-25 18:29:33). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; `timenow > time + ...` is always true on history. |
| 2 | PASS | Indicator levels and percentages (the pending trail's tick scaling aside). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, pyramiding 100 and the trail quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`per` [23, 46] x `mult` [1.5, 2.5] x `adx_th` [8, 20]: **8 trials**; defaults 23 / 1.5 / 8 (the source's); T3, SAR, RSI, MACD and trail settings fixed.

## Trailing stop (mark `trailing_stop_pending`)

`strategy.exit(trail_points = |entry x 0.5 %| x 2, trail_offset = high x ts % x 2)` in ticks, with ts growing from 0.25 % to 1 % as the profit grows: a profit-dependent offset on tick-scaled distances, not expressible in the house spec; not ported. The trailing flags (long_ts / short_ts) that feed the entry and close state machines ARE ported, as written.

## Ambiguities resolved

- All state machines (CondIni_*, X conditions, last_* stamps) ported as written; anti-liquidation flags reach no order.
- Division by zero (entry price 0 before the first signal) is na.
- Adds (pyramiding 100) are sizing. Entry wins over a same-bar close_all. Start-year filter dropped.
- Broker-day bars; FREQ = "1D". REVERSAL INTENDED.

## Decision owed

The intended trailing exit (its "pips correction" 2 suggests the author meant price distances).

## FAMILY (proposed, user to confirm)

`FAMILY = "range_filter_trend"`.

## Marks

`trailing_stop_pending`

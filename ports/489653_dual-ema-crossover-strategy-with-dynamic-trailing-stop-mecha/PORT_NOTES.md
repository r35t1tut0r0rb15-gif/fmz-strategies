# #489653 双指数均线交叉与尾随止损结合的量化交易策略-Dual-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop-Mechanism -> `fmz_489653_ema13_33_side_tick_trail_2d`

- FMZ source id: 489653 (lineage).
- Source: https://www.fmz.com/strategy/489653 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-07 13:39:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail a house trail (approximation stated). |
| 2 | ADAPT | 2-tick trail -> a fraction of price; the price-unit activation is immediate. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 20 % of equity quoted; the trail via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND489653 (2 members, best partner #489737, Jaccard 0.651). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.000007, 0.01] x `long_ema` [33, 50]: **4 trials**; defaults 0.000007 / 33; EMA 13 / 25 fixed.

## Trailing stop (mark `trailing_stop`)

As #489737: `strategy.exit(trail_offset = 2, trail_price = high - 10)` every bar while in a trade, ported as the
house trail `{"type": "percent", "pct": 0.000007, "anchor": "high_low"}` with no activation. Promotion of a
trailing trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- Unlike #489737 the EMA exits run. exitLong implies the short condition; exitShort is a short exit on bars without
  a short entry (when both hold the from-flat reading is taken: the trail closes nearly every trade within its first
  bar; stated approximation).
- Two-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509: `coarse_bar_stop`.
- REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop, trailing_stop`

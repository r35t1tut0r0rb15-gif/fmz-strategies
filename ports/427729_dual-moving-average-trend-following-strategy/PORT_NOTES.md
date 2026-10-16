# #427729 Dual Moving Average Trend Following Strategy -> `fmz_427729_pb_trend_scalper`

- FMZ source id: 427729 (lineage).
- Source: https://www.fmz.com/strategy/427729 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-24 13:14:08). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C11) AS WRITTEN. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; take-profit fixed at entry. |
| 2 | ADAPT | Tick-scaled take-profit -> percentage. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Leveraged quantity stored; take-profit quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [69, 6.9] x `zone` [3, 1.5] x `longma` [100, 200]: **8 trials**; defaults 69 (as written on BTC with a 0.1 tick) / 3 / 100; EMA 55 and the 170-bar extremes fixed.

## Ambiguities resolved

- `profit = position_avg_price x 6.9` is in ticks: about 69 % on BTC_USDT. Ported as written; 6.9 % in the grid.
- Long may reverse a short (opentrades <= 1); short only from flat; the flat test follows the house take-profit.
- Closes are market exit signals on the bar's range. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. Stops on 3-hour bars: mark `coarse_bar_stop`. FREQ = "3h".

## Decision owed

Intended take-profit: probably 6.9 % of the average price (in the grid already).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop`

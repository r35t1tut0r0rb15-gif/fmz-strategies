# #482846 双均线止盈止损趋势交易策略-Dual-Moving-Average-Trend-Trading-Strategy-with-Stop-Loss-and-Take-Profit -> `fmz_482846_sma9_21_golden_cross_pct_bracket_long`

- FMZ source id: 482846 (lineage).
- Source: https://www.fmz.com/strategy/482846 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:36:23). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill (decision owed). |
| 2 | PASS | Moving averages and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 3.0] x `tp_pct` [1.0, 3.0]: **4 trials**; defaults 1 / 1 (the source's); SMA 9 / 21 fixed.

## Bracket from strategy.position_avg_price (decision owed)

The exit is issued only on the golden-cross bar from `strategy.position_avg_price`, na while flat, and crosses
alternate, so as written no stop or target is ever placed. The port applies the 1 % / 1 % bracket from the fill (the
evident intent), as #489289. Decision owed: keep this, or port the literal cross-only exits.

## Ambiguities resolved

- Long only: opposite entries cannot occur; the death cross is an exit signal. Stop module: `portfolio_kwargs` {}
  (D4). Broker days stamped with their first minute (as #430984); `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

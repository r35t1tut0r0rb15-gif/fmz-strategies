# #483679 双均线交叉与随机指标结合的自适应追踪止损策略-Dual-Moving-Average-Crossover-with-Stochastic-Filter-and-Adaptive-Trailing-Stop-Strategy -> `fmz_483679_sma34_200_stoch_cross_pct_bracket`

- FMZ source id: 483679 (lineage).
- Source: https://www.fmz.com/strategy/483679 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-25 11:05:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the fill (re-placement marked). |
| 2 | PASS | Moving averages, a stochastic and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [2.0, 3.0] x `tp_pct` [4.0, 6.0]: **4 trials**; defaults 2 / 4 (the source's); SMA 34 / 200 and the
stochastic 9 / 3 fixed.

## Bracket from strategy.position_avg_price (decision owed)

The exit is issued only on signal bars, from `strategy.position_avg_price`, which is na while flat: a trade opened from
flat therefore has no stop or target until a later same-side signal re-issues the exit (that entry being ignored). The
port applies the 2 % / 4 % bracket from the fill (the evident intent), as #489289. Decision owed: keep this, or port
the literal behaviour.

## Trailing stop (mark `trailing_stop_pending`)

A re-issued exit moves the stop to the entry price once the close is 2 % in profit (checked only on signal bars). The
port keeps the entry's bracket.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

# #427592 Bollinger Band Breakout Trend Following Strategy -> `fmz_427592_bb_breakout_pct_trail`

- FMZ source id: 427592 (lineage).
- Source: https://www.fmz.com/strategy/427592 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-22 14:31:17). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; stop and trail as house stops (approximation stated). |
| 2 | PASS | Bands in standard deviations, percent distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity / leverage quantity stored; stops quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.2, 2] x `trail_pct` [0.5, 2] x `activate` [5, 2.5]: **8 trials**; defaults 1.2 / 0.5 / 5 (the source's); SMA 20 and the 7.5 % stop fixed.

## Trailing stop (FMZ-C rule 1, mark `trailing_stop`)

As written: `strategy.exit(loss = close x 7.5 %, trail_points = close x 5 %, trail_offset = close x 0.5 %)` in ticks, re-issued every bar. Ported as `sl_stop` 0.075 plus the house trail `{"type": "percent", "pct": 0.005, "anchor": "high_low", "activate_after": 0.05}`. **Stated approximation:** Pine scales the distances by the current close each bar, the house by the entry / best price; the difference is the price move times the small percentage. Promotion of a trailing trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- The year window and the leverage quantity are dropped / sizing; `barstate.isconfirmed` is true on history.
- Broker-day bars; daily stops: mark `coarse_bar_stop`. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`, `trailing_stop`

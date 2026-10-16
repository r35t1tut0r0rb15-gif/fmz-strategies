# #427990 Eltrut Turtle Reversal Strategy -> `fmz_427990_eltrut_trendflex_long`

- FMZ source id: 427990 (lineage).
- Source: https://www.fmz.com/strategy/427990 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-27 16:30:51). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15) AS WRITTEN. Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Channel lengths, standard deviations and percentages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Slippage / commission settings stored; exits quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [3, 1.5] x `take_pct` [9, 4.5]: **4 trials**; defaults 3 / 9 (the source's); channel 7, flex 20, BB 35 x 3 fixed.

## Ambiguities resolved

- Both signals call `strategy.entry("Long", strategy.long, ...)`: as written the strategy is long only.
- IQIFM is never called; the reflex series is unused. `sl_stop` 0.03, `tp_stop` 0.09.
- Stop module: `portfolio_kwargs` `{}`. Stops on 4-hour bars: mark `coarse_bar_stop`. FREQ = "4h".

## Decision owed

Intended version: the breakout above the 7-bar high enters short.

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_reversal"`.

## Marks

`coarse_bar_stop`

# #489893 Multi Factor Mean Reversion Strategy A Mean Reversion Trading System Combining Stochastic RSI and Bollinger Bands -> `fmz_489893_stochrsi14_extreme_bb20_2_touch_flat`

- FMZ source id: 489893 (lineage).
- Source: https://www.fmz.com/strategy/489893 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-09 17:05:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C272). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI extremes at the Bollinger bands |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `bbLength` [20, 50]: **4 trials**; K / D 3, BB 2, levels as written.

## Ambiguities resolved

- The levels are on the wrong scale, as written. Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic"`.

## Marks

`none`

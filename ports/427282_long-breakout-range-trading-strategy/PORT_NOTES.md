# #427282 Long Breakout Range Trading Strategy -> `fmz_427282_breakout_range_long`

- FMZ source id: 427282 (lineage).
- Source: https://www.fmz.com/strategy/427282 (PineScript (no @version line, v1 syntax), author ChaoZhang, FMZ last
  modified 2023-09-19 17:19:55). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar counts only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`look_back` [4, 8, 16]: **3 trials**; default 4 (the source's).

## Ambiguities resolved

- The breakout compares with the 4 bars before the current one (`highest(high, 4)[1]`).
- Long only ("reverse" off). FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`

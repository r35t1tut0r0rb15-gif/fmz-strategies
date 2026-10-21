# #439083 基于Fibonacci水平的日内高低价突破Breakthrough-of-Daily-High-low-Price-Based-on-Fibonacci-Levels -> `fmz_439083_day_first_bar_level_cross_long`

- FMZ source id: 439083 (lineage).
- Source: https://www.fmz.com/strategy/439083 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 15:59:17). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | First-bar day levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`exit_on_low` [True, False] x `buffer` [0.0, 0.001]: **4 trials**; False closes on a cross under the first-bar high; buffer is a fraction of the level.

## Ambiguities resolved

- First-bar levels as written. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`

# #483089 Dynamic Breakout Falling Wedge Trendline Quantitative Trading Strategy -> `fmz_483089_falling_wedge_pivot5_upper_line_break_2_20pct_bracket_long`

- FMZ source id: 483089 (lineage).
- Source: https://www.fmz.com/strategy/483089 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:02:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C256). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | Falling-wedge trendline breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_bars` [5, 3] x `take_profit_percent` [20.0, 10.0]: **4 trials**; left = right bars, stop 2 %.

## Ambiguities resolved

- The upper line exists only while the wedge test holds; its crossover needs it on the previous bar.
- A repeat breakout's re-sent bracket is pending. MPL 2.0 source, ported and stated. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

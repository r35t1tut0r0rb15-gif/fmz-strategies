# #427275 Quantitative Trading Strategy Based on Voss Filter and Trend Indicator -> `fmz_427275_voss_instantaneous_trend`

- FMZ source id: 427275 (lineage).
- Source: https://www.fmz.com/strategy/427275 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 16:59:10). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; recursive filters on past bars. |
| 2 | PASS | Linear filters of price; crosses are scale-free. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 40] x `predict` [4, 2] x `alpha` [0.07, 0.15]: **8 trials**; defaults 20 / 4 / 0.07 (the source's); bandwidth 0.25 fixed.

## Ambiguities resolved

- Both entries need `lag < it` (written once as `it > lag`), as in the source.
- The filter is 0 until bar_index > order (counted from the data's first bar); nz() seeds as written.
- `isPeriod = true`: the window close-out never fires. The short entry is tested first (script order). REVERSAL INTENDED.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`

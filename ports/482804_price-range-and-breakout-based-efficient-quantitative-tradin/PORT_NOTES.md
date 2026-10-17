# #482804 基于价格区间和突破的高效量化交易策略Price-Range-and-Breakout-Based-Efficient-Quantitative-Trading-Strategy -> `fmz_482804_pivot_consolidation_zone_breakout_5d`

- FMZ source id: 482804 (lineage).
- Source: https://www.fmz.com/strategy/482804 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:46:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Rolling extremes and pivot-defined ranges. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`prd` [10, 20] x `conslen` [5, 10]: **4 trials**; defaults 10 / 5 (the source's).

## Ambiguities resolved

- `highestbars(prd) == 0`: the bar's high equals the window's highest (ties count as the current bar).
- `pp`: the extreme pivot of the current direction run (the 1000-bar loop stops where `dir` changes); with `dir` 0
  the latest pivot. `ta.change(pp)` with na on either side counts as no change.
- The zone (condhigh / condlow) keeps its last values after the counter resets, as the `var`s do.
- REVERSAL INTENDED (always in). Five-day bars: blocks of broker-day dates from 1970-01-01 (decision owed, #426509).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

none

# #482826 高级多重形态突破交易策略-Advanced-Multi-Pattern-Breakout-Trading-Strategy -> `fmz_482826_candle_pattern_breakouts_always_in`

- FMZ source id: 482826 (lineage).
- Source: https://www.fmz.com/strategy/482826 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 13:33:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle proportions and prior-bar extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`GRID = {}`: **1 trial**. The source has no signal parameter (the lookback input only feeds drawings).

## Ambiguities resolved

- Pattern tests as written (the hammer's shadows from open and close).
- All long entries share one position (pyramiding 1), as do the shorts. REVERSAL INTENDED (always in).
- A bar with both a long and a short pattern emits neither (rare; the order of the two reversals is ambiguous).
- Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

none

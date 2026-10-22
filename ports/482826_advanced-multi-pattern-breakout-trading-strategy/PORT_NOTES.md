# #482826 Advanced Multi Pattern Breakout Trading Strategy -> `fmz_482826_green_red_pair_doji_hammer_pin_prev_bar_break_reversal`

- FMZ source id: 482826 (lineage).
- Source: https://www.fmz.com/strategy/482826 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 13:33:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle-shape breakouts of the previous bar |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

GRID = {}: No parameter reaches the orders: **1 trial**, the source as written (lookbackPeriod feeds the target boxes only).

## Ambiguities resolved

- Same-id repeat longs are refused (pyramiding default); the later short call wins on a shared bar.
- REVERSAL INTENDED, no other exit. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

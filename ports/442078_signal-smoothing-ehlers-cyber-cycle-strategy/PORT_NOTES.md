# #442078 Signal Smoothing Ehlers Cyber Cycle Strategy -> `fmz_442078_ehlers_cyber_cycle_turn_opposite_reversal`

- FMZ source id: 442078 (lineage).
- Source: https://www.fmz.com/strategy/442078 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-19 10:42:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C150). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Cycle signal turns and a close-vs-fill loss test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND439084. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`alpha` [0.07, 0.15] x `lag` [9, 5]: **4 trials**; the 8-bar loss rule fixed.

## Ambiguities resolved

- Opposite-trade default; sign-only openprofit as close vs fill. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "cycle_filter"`.

## Marks

`none`

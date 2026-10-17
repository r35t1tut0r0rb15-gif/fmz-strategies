# #433574 Ichimoku Kumo Twist Gold Absorbing Strategy -> `fmz_433574_kumo_twist`

- FMZ source id: 433574 (lineage).
- Source: https://www.fmz.com/strategy/433574 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-28 16:12:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku line crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`preset` ["Cpt 20 60 120 30", "Std 9 26 52 26"]: **2 trials** (the author's own preset list, first and last).

## Ambiguities resolved

- Current-bar lead lines; partial windows at the start as written. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

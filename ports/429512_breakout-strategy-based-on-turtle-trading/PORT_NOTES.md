# #429512 Breakout Strategy Based on Turtle Trading -> `fmz_429512_turtle_donchian_long`

- FMZ source id: 429512 (lineage).
- Source: https://www.fmz.com/strategy/429512 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-17 17:22:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits. |
| 2 | PASS | Channel levels and an ATR distance. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1-unit quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`enter_period` [20, 55] x `exit_period` [10, 20]: **4 trials**; ATR 20 fixed.

## Ambiguities resolved

- Close-checked exits. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`

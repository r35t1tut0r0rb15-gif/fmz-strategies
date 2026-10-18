# #436242 Oscillator Index Transformation Strategy -> `fmz_436242_three_ten_oscillator_state`

- FMZ source id: 436242 (lineage).
- Source: https://www.fmz.com/strategy/436242 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-22 14:21:28). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator against its signal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `length2` [10, 15]: **4 trials**; EMA 3 and signal 16 fixed.

## Ambiguities resolved

- State changes only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

# #438795 Aroon Oscillator Based Stock Trading Strategy -> `fmz_438795_aroon_oscillator_middle_cross`

- FMZ source id: 438795 (lineage).
- Source: https://www.fmz.com/strategy/438795 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-15 14:08:33). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Aroon oscillator levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [19, 25] x `level_middle` [-25, 0]: **4 trials**; 75 / -85 exit levels fixed.

## Ambiguities resolved

- Ties in highestbars take the most recent bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

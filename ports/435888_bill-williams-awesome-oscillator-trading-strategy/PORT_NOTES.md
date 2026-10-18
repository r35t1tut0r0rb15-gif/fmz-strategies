# #435888 Bill Williams Awesome Oscillator Trading Strategy -> `fmz_435888_awesome_oscillator_slope`

- FMZ source id: 435888 (lineage).
- Source: https://www.fmz.com/strategy/435888 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-19 15:27:15). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND435250. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `slow` [34, 21]: **4 trials**; fast 5 fixed.

## Ambiguities resolved

- State changes only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

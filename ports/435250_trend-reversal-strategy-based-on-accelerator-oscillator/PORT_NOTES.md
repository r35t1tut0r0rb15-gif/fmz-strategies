# #435250 Trend Reversal Strategy Based on Accelerator Oscillator -> `fmz_435250_accelerator_oscillator_sign`

- FMZ source id: 435250 (lineage).
- Source: https://www.fmz.com/strategy/435250 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-13 15:38:12). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG435250, ND435250. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `slow` [34, 21]: **4 trials**; fast 5 fixed.

## Ambiguities resolved

- State changes only. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

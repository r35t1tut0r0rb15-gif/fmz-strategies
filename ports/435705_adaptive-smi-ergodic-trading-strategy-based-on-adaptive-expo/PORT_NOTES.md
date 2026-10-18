# #435705 Adaptive SMI Ergodic Trading Strategy Based on Adaptive Exponential Moving Average Lines -> `fmz_435705_tsi_signal_cross`

- FMZ source id: 435705 (lineage).
- Source: https://www.fmz.com/strategy/435705 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-18 10:34:55). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | True strength index crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`longlen` [12, 25] x `siglen` [5, 9]: **4 trials**; short length 5 and the +-0.4 levels fixed.

## Ambiguities resolved

- tsi as the Pine definition. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

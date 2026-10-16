# #430740 SMI Ergodic Oscillator Momentum Trading Strategy -> `fmz_430740_smi_ergodic_bands`

- FMZ source id: 430740 (lineage).
- Source: https://www.fmz.com/strategy/430740 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-01 11:19:18). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A bounded momentum ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG430740. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow_period` [8, 20] x `band` [0.5, 0.3]: **4 trials**; fast 4 and smoothing 3 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`

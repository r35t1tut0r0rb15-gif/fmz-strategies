# #449698 Stochastic Crossover Indicator Momentum Trading Strategy -> `fmz_449698_stoch_cross_at_extremes_reversal`

- FMZ source id: 449698 (lineage).
- Source: https://www.fmz.com/strategy/449698 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-28 11:57:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic crossings at the extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 9] x `smooth` [3, 5]: **4 trials**; the levels fixed (one smoothing for K and D, as their defaults agree).

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`

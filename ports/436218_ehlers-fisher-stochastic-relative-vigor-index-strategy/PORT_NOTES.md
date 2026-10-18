# #436218 Ehlers Fisher Stochastic Relative Vigor Index Strategy -> `fmz_436218_fisher_stochastic_rvi`

- FMZ source id: 436218 (lineage).
- Source: https://www.fmz.com/strategy/436218 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-22 12:04:23). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exit on closes |
| 2 | PASS | Fisher stochastic of a vigor index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p` [10, 14] x `opposite_trade` [True, False]: **4 trials**.

## Ambiguities resolved

- Open profit from the next-open fill; barsSinceEntry loop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

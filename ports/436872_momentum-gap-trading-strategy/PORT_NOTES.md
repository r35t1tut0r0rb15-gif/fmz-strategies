# #436872 Momentum Gap Trading Strategy -> `fmz_436872_gap_momentum_long_only`

- FMZ source id: 436872 (lineage).
- Source: https://www.fmz.com/strategy/436872 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-28 14:38:33). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C96). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ratio of gap sums |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [40, 20] x `signal_period` [20, 10]: **4 trials**; long only.

## Ambiguities resolved

- Short branch off and not ported. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

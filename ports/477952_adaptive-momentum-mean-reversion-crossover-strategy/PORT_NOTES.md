# #477952 Adaptive Momentum Mean Reversion Crossover Strategy -> `fmz_477952_roc2_bollinger_lower_cross_upper_exit_long`

- FMZ source id: 477952 (lineage).
- Source: https://www.fmz.com/strategy/477952 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-10 15:26:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ROC band re-entries and exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital stored; costs not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_period` [2, 5] x `lower_sd` [1.7, 2.0]: **4 trials**; lower length 18, upper 21 / 2.1.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

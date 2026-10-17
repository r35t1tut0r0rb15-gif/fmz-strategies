# #482919 Triple-EMA和Fisher-Transform趋势动量策略-Triple-EMA-and-Fisher-Transform-Trend-Momentum-Strategy -> `fmz_482919_tema_fisher_joint_cross_1d`

- FMZ source id: 482919 (lineage).
- Source: https://www.fmz.com/strategy/482919 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 17:41:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | TEMA and a Fisher transform. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tema_len` [21, 34] x `fisher_len` [10, 20]: **4 trials**; defaults 21 / 10 (the source's); smoothing 1 (off).

## Ambiguities resolved

- The Fisher input value is not smoothed recursively (only the transform), as written.
- Closes act on the position held at the bar's start and never undo that bar's entry (as #430850).
- REVERSAL INTENDED. No stops. Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_cross"`.

## Marks

`none`

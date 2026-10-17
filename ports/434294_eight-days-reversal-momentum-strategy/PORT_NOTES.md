# #434294 Eight Days Reversal Momentum Strategy -> `fmz_434294_eight_bar_run_reversal`

- FMZ source id: 434294 (lineage).
- Source: https://www.fmz.com/strategy/434294 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-05 10:56:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Runs against a short average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [5, 10] x `run` [8, 5]: **4 trials**.

## Ambiguities resolved

- barssince na until first occurrence; same-bar entry beats the close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`none`

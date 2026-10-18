# #435852 Eight Day Extended Run Strategy -> `fmz_435852_run_exhaustion_fade`

- FMZ source id: 435852 (lineage).
- Source: https://www.fmz.com/strategy/435852 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-19 12:01:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average run counts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [5, 10] x `run` [8, 5]: **4 trials**; the exit after 10 bars fixed.

## Ambiguities resolved

- Time exit as an explicit exit signal. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

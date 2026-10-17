# #431392 Gaussian Detrended Reversion Trading Strategy -> `fmz_431392_gaussian_dpo_reversion`

- FMZ source id: 431392 (lineage).
- Source: https://www.fmz.com/strategy/431392 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-07 15:01:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A smoothed detrended oscillator |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 15 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [50, 100] x `lag` [25, 10]: **4 trials**; ALMA 50 / 0.85 / 6 fixed.

## Ambiguities resolved

- Close conventions as stated. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`none`

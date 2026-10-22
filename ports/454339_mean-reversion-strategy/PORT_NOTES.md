# #454339 Mean Reversion Strategy -> `fmz_454339_sma20_sd_band_reentry_basis_exit_reversal`

- FMZ source id: 454339 (lineage).
- Source: https://www.fmz.com/strategy/454339 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 14:57:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band re-entries with basis exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [1.5, 2.0]: **4 trials**.

## Ambiguities resolved

- Call order. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

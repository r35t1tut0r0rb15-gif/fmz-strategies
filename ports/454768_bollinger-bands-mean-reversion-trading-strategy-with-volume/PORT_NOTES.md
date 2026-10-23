# #454768 Bollinger Bands Mean Reversion Trading Strategy with Volume Filter -> `fmz_454768_bollinger_reentry_reversal_1h`

- FMZ source id: 454768 (lineage).
- Source: https://www.fmz.com/strategy/454768 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 18:20:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- The absolute volume filter only repeats orders already sent. Volume not used. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

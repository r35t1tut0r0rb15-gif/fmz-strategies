# #441102 Dual Smoothed Stochastic Bressert Strategy -> `fmz_441102_dss_bressert_zone_state_reversal`

- FMZ source id: 441102 (lineage).
- Source: https://www.fmz.com/strategy/441102 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-05 15:57:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Double-smoothed stochastic states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pds` [10, 14] x `ema_len` [9, 5]: **4 trials**; trigger 5 and levels fixed.

## Ambiguities resolved

- States as written. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`

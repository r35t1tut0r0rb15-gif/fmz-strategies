# #442221 Rate of Change Optimization Strategy -> `fmz_442221_normalised_roc_turn_long`

- FMZ source id: 442221 (lineage).
- Source: https://www.fmz.com/strategy/442221 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 13:54:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Normalised ROC turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [9, 14] x `max_history` [200, 100]: **4 trials**; smoothing and thresholds fixed.

## Ambiguities resolved

- Ratio as written. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

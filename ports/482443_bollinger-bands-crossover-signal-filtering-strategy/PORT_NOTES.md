# #482443 Bollinger Bands Crossover Signal Filtering Strategy -> `fmz_482443_bb55_1sd_break_side_switch_reversal`

- FMZ source id: 482443 (lineage).
- Source: https://www.fmz.com/strategy/482443 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 14:47:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C244). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger break-side switches |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [55, 20] x `mult` [1.0, 2.0]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`

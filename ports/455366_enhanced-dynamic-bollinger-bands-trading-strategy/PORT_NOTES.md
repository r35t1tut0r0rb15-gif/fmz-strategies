# #455366 Enhanced Dynamic Bollinger Bands Trading Strategy -> `fmz_455366_bollinger34_two_sd_state_reversal`

- FMZ source id: 455366 (lineage).
- Source: https://www.fmz.com/strategy/455366 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-28 15:31:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Two-deviation band states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND455366. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 20] x `mult` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`

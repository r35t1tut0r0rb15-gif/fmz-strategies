# #455359 Multi Moving Average Crossover Trend Following Strategy -> `fmz_455359_tillson_t3_turn_reversal`

- FMZ source id: 455359 (lineage).
- Source: https://www.fmz.com/strategy/455359 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-06-28 15:10:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | T3 turns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [8, 14] x `vfactor` [0.7, 0.5]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`

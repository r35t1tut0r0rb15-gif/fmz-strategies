# #443106 Momentum Average Directional Movement Index Moving Average Crossover Strategy -> `fmz_443106_adx15_di_direction_long`

- FMZ source id: 443106 (lineage).
- Source: https://www.fmz.com/strategy/443106 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 11:50:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX direction with a floor |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`di_length` [14, 7] x `adx_active` [15, 25]: **4 trials**; the ADX smoothing fixed.

## Ambiguities resolved

- Double-smoothed range as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`

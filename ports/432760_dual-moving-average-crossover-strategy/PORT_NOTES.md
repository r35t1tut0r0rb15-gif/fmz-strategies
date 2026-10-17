# #432760 Dual Moving Average Crossover Strategy -> `fmz_432760_ema_river_flip`

- FMZ source id: 432760 (lineage).
- Source: https://www.fmz.com/strategy/432760 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-21 11:34:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Open and close against two EMAs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [10, 5] x `ma2` [20, 40]: **4 trials**; both EMA.

## Ambiguities resolved

- Closes after the entries do not undo the flip. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

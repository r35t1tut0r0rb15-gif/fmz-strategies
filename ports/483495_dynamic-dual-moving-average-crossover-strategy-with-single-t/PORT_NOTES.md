# #483495 Dynamic Dual Moving Average Crossover Strategy with Single Trade Execution System using Exponential Moving Averages -> `fmz_483495_ema9_21_cross_long`

- FMZ source id: 483495 (lineage).
- Source: https://www.fmz.com/strategy/483495 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-24 09:15:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C258). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_period9` [9, 5] x `ema_period21` [21, 50]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

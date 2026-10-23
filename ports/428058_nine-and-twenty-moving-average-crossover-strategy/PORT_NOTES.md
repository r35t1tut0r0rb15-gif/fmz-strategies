# #428058 Nine and Twenty Moving Average Crossover Strategy -> `fmz_428058_ema9_20_cross_daily_reversal`

- FMZ source id: 428058 (lineage).
- Source: https://www.fmz.com/strategy/428058 (PineScript v1, author ChaoZhang, FMZ last
  modified 2023-09-28 11:17:10). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossover |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428058. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [20, 50]: **4 trials**.

## Ambiguities resolved

- VWAP only plotted. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_crossover"`.

## Marks

`none`

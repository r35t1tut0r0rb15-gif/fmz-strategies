# #439735 Adaptive Moving Average and Weighted Moving Average Crossover Trading Strategy -> `fmz_439735_wma21_nested_ema14_cross`

- FMZ source id: 439735 (lineage).
- Source: https://www.fmz.com/strategy/439735 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-23 14:13:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | WMA / nested EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`aioma_length` [14, 7] x `wma_length` [21, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

# #442558 基于价格与SMA交叉的量化交易策略Quantitative-Trading-Strategy-Based-on-Price-Crossover-with-SMA -> `fmz_442558_close_sma21_cross_long`

- FMZ source id: 442558 (lineage).
- Source: https://www.fmz.com/strategy/442558 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 17:34:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [21, 50]: **2 trials**.

## Ambiguities resolved

- Same-time-frame request read as the chart's close. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

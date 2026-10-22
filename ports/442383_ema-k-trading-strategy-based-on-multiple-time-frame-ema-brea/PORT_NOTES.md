# #442383 多时间框架EMA突破与K线形态组合策略Trading-Strategy-Based-on-Multiple-Time-Frame-EMA-Breakthrough-and-K-line-Pattern-Combination -> `fmz_442383_last_2h_bar_direction_flip_long`

- FMZ source id: 442383 (lineage).
- Source: https://www.fmz.com/strategy/442383 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-21 15:00:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 2-hour values end with the daily bar |
| 2 | PASS | Last-2-hour-bar direction flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tf_minutes` [120, 240]: **2 trials**.

## Ambiguities resolved

- Last 2-hour bar of the broker day (as #436765). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

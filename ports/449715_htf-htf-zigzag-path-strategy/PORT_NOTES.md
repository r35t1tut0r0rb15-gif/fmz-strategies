# #449715 HTF-锯齿形路径策略HTF-Zigzag-Path-Strategy -> `fmz_449715_last_15m_bar_colour_contrarian_reversal`

- FMZ source id: 449715 (lineage).
- Source: https://www.fmz.com/strategy/449715 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-28 14:00:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 15-minute bar ends with the daily bar |
| 2 | PASS | Contrarian colour of the day's last 15-minute bar |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tf_minutes` [15, 60]: **2 trials**.

## Ambiguities resolved

- Last 15-minute bar of each broker day. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

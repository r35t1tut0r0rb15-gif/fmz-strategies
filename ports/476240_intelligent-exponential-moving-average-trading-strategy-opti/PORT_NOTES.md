# #476240 Intelligent Exponential Moving Average Trading Strategy Optimization System -> `fmz_476240_close_cross_ema9_ema21_trend_reversal`

- FMZ source id: 476240 (lineage).
- Source: https://www.fmz.com/strategy/476240 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 13:56:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C230). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA close crossings with an EMA trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_short` [9, 5] x `ema_long` [21, 50]: **4 trials**.

## Ambiguities resolved

- A close after a reversing entry on one bar leaves the reversal. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

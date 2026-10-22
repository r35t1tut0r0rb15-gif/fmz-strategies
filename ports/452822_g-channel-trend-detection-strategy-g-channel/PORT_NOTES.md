# #452822 G-Channel-Trend-Detection-Strategy-G-Channel趋势检测策略 -> `fmz_452822_g_channel_trend_flip_reversal`

- FMZ source id: 452822 (lineage).
- Source: https://www.fmz.com/strategy/452822 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-29 17:06:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C190). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the per-bar bracket pending (mark) |
| 2 | PASS | G-Channel trend flips |
| 3 | PASS | No exchange named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50]: **2 trials**.

## Ambiguities resolved

- No bar size (bar_size_pending); the per-bar bracket pending. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`bar_size_pending, trailing_stop_pending`

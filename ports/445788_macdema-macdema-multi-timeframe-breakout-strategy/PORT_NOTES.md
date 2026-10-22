# #445788 MACDEMA多时间尺度突破策略MACDEMA-Multi-Timeframe-Breakout-Strategy -> `fmz_445788_weekly_macd_dir_daily_ema_break_reversal`

- FMZ source id: 445788 (lineage).
- Source: https://www.fmz.com/strategy/445788 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 11:13:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks |
| 2 | PASS | Weekly MACD direction with daily EMA breakouts and a loss exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital stored; the cash commission is a cost, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`loss_frac` [0.00238, 0.01] x `week_ema` [3, 6]: **4 trials**; the daily EMAs and the weekly MACD fixed.

## Ambiguities resolved

- 100 points as 0.00238 of the fill; weekly values from completed weeks. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`

# #478724 Advanced Multi Indicator Multi Dimensional Trend Cross Quantitative Strategy -> `fmz_478724_ema50_100_cross_cloud_rsi_macd_daily_level_flags_reversal`

- FMZ source id: 478724 (lineage).
- Source: https://www.fmz.com/strategy/478724 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 16:00:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | EMA crossings with cloud, RSI, MACD and daily-level filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [50, 20] x `ema_slow` [100, 50]: **4 trials**; Ichimoku 9 / 26 / 52, RSI 14, MACD 12 / 26 / 9, EMA 200.

## Ambiguities resolved

- Daily RSI / MACD from the last completed broker day; flags kept as written. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

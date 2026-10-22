# #449971 MACD-RSI-一目均衡Ichimoku动量趋势多头策略-MACD-RSI-Ichimoku-Momentum-Trend-Following-Long-Strategy -> `fmz_449971_sma_ichimoku_cross_or_cloud_macd_rsi_long`

- FMZ source id: 449971 (lineage).
- Source: https://www.fmz.com/strategy/449971 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 17:42:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C183). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; Span A from 26 bars back |
| 2 | PASS | Ichimoku-style crossings and cloud side with MACD / RSI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [9, 20] x `len2` [26, 50]: **4 trials**; the span length 52 and the MACD / RSI settings fixed.

## Ambiguities resolved

- SMA-based lines as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

# #474847 趋势波段交易EMA-MACD复合策略-EMA-MACD-Composite-Strategy-for-Trend-Scalping -> `fmz_474847_ema50_200_trend_rsi_macd_state_reversal`

- FMZ source id: 474847 (lineage).
- Source: https://www.fmz.com/strategy/474847 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-12 15:05:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend / momentum states with state-end closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; RSI / MACD fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

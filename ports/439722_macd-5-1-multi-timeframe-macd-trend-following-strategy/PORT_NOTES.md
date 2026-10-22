# #439722 MACD-5合1多指标趋势追踪策略Multi-timeframe-MACD-Trend-Following-Strategy -> `fmz_439722_macd_signal_cross_long_stgy1`

- FMZ source id: 439722 (lineage).
- Source: https://www.fmz.com/strategy/439722 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 12:08:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 21]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- Strategy 1 only. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`

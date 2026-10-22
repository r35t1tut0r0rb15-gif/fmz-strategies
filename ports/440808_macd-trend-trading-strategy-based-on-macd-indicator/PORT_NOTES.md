# #440808 基于MACD指标的趋势交易策略-Trend-Trading-Strategy-Based-on-MACD-Indicator -> `fmz_440808_trend_trader_line_macd_filter`

- FMZ source id: 440808 (lineage).
- Source: https://www.fmz.com/strategy/440808 (PineScript v1, author ChaoZhang, FMZ last
  modified 2024-02-02 11:32:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing line and MACD histogram |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `multiplier` [3, 2]: **4 trials**; MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`

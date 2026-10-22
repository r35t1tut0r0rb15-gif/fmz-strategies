# #439603 低风险DCA趋势交易策略Low-Risk-DCA-Trend-Trading-Strategy -> `fmz_439603_rsi_extreme_engulfing_long`

- FMZ source id: 439603 (lineage).
- Source: https://www.fmz.com/strategy/439603 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-22 10:20:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes and engulfing closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash-per-trade quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `rsi_oversold` [30, 40]: **4 trials**; overbought 70 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

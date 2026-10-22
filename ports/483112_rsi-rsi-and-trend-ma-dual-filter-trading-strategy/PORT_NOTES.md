# #483112 基于RSI和趋势均线的双重过滤交易策略-RSI-and-Trend-MA-Dual-Filter-Trading-Strategy -> `fmz_483112_rsi14_30_70_cross_sma200_side_reversal`

- FMZ source id: 483112 (lineage).
- Source: https://www.fmz.com/strategy/483112 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:05:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI level crossings with an SMA trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `ma_length` [200, 100]: **4 trials**; levels 30 / 70.

## Ambiguities resolved

- REVERSAL INTENDED, no other exit. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

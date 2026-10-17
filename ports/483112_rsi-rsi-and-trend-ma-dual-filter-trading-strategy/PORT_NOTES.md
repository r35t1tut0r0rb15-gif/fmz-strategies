# #483112 基于RSI和趋势均线的双重过滤交易策略-RSI-and-Trend-MA-Dual-Filter-Trading-Strategy -> `fmz_483112_rsi_exit_extreme_sma200_reversal`

- FMZ source id: 483112 (lineage).
- Source: https://www.fmz.com/strategy/483112 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:05:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI and a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`use_trend_filter` [True, False] x `ma_len` [200, 100]: **4 trials**; defaults True / 200 (the source's); RSI 14
(30 / 70) fixed.

## Ambiguities resolved

- close + entry on the same signal is a reversal: only the entries are emitted. No stops.
- REVERSAL INTENDED. FREQ = "1min" ("Daily Signals" is a label).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

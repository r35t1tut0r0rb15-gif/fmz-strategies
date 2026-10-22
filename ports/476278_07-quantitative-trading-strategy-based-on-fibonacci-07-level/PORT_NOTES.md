# #476278 基于斐波那契07水平的趋势突破量化交易策略-Quantitative-Trading-Strategy-Based-on-Fibonacci-07-Level-Trend-Breakthrough -> `fmz_476278_fib07_range_cross_pct_bracket_reversal`

- FMZ source id: 476278 (lineage).
- Source: https://www.fmz.com/strategy/476278 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 15:51:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price bracket as fractions of the fill |
| 2 | PASS | Range-retracement crossings with a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 50] x `tp_pct` [0.018, 0.036]: **4 trials**; stop 1.2 %.

## Ambiguities resolved

- The previous close is compared with the current level, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`

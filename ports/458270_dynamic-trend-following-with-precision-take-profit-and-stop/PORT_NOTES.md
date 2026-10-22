# #458270 Dynamic Trend Following with Precision Take Profit and Stop Loss Strategy -> `fmz_458270_three_candle_burst_range_levels_close_tests_reversal`

- FMZ source id: 458270 (lineage).
- Source: https://www.fmz.com/strategy/458270 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:27:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the target and stop are close tests |
| 2 | PASS | Three-candle bursts with range and trend filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`filter_number` [1.5, 1.0] x `trend_len` [50, 100] x `lookback` [20, 10]: **8 trials**.

## Ambiguities resolved

- Levels per side as written; exits are close tests. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`

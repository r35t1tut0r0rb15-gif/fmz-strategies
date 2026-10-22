# #483122 Multi Layer Moving Average Cross Precise Timing Trend Following Strategy -> `fmz_483122_bar_range_sma50_cross_stacked_trend_sma20_exit_reversal`

- FMZ source id: 483122 (lineage).
- Source: https://www.fmz.com/strategy/483122 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:32:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C258). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bar-range SMA crossings in a stacked trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_period1` [20, 10] x `sma_period2` [50, 30]: **4 trials**; SMA 100 / 200.

## Ambiguities resolved

- Default tick-precise crosses. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

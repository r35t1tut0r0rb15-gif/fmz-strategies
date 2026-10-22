# #483123 趋势跟踪型双均线交叉策略结合SMA趋势过滤系统-Trend-Following-Dual-EMA-Crossover-Strategy-with-SMA-Trend-Filtering-System -> `fmz_483123_ema9_21_cross_sma15_side_candles_bar_stop_4r_reversal`

- FMZ source id: 483123 (lineage).
- Source: https://www.fmz.com/strategy/483123 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:35:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C258). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an SMA side and candle filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [15, 30] x `rr` [4.0, 2.0]: **4 trials**; EMA 9 / 21.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4D" (four broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

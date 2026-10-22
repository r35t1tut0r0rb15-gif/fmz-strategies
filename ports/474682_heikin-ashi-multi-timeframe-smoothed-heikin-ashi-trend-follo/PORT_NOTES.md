# #474682 多周期平滑Heikin-Ashi趋势跟踪量化交易系统-Multi-Timeframe-Smoothed-Heikin-Ashi-Trend-Following-Quantitative-Trading-System -> `fmz_474682_sma2_open_close_colour_avg_bracket_long`

- FMZ source id: 474682 (lineage).
- Source: https://www.fmz.com/strategy/474682 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 15:42:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the average-price bracket as fixed fractions |
| 2 | PASS | Two-bar average colour with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.02, 0.04] x `tp_pct` [0.04, 0.08]: **4 trials**; Buy Only.

## Ambiguities resolved

- "D" equals the chart (no lookahead effect). Buy Only (default). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`

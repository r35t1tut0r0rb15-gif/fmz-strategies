# #483525 基于动量增强型简单移动平均线和RSI的趋势跟踪策略-Momentum-Enhanced-Simple-Moving-Average-and-RSI-Strategy-for-Trend-Following -> `fmz_483525_sma8_21_cross_rsi_filter_1_2pct_bracket_reversal`

- FMZ source id: 483525 (lineage).
- Source: https://www.fmz.com/strategy/483525 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-24 10:19:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | SMA crossings with RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_length` [8, 5] x `long_length` [21, 50]: **4 trials**; RSI 14 / 70 / 30, stop 1 %, target 2 %.

## Ambiguities resolved

- The bracket is ported from the fill, active from the fill bar. REVERSAL INTENDED. FREQ = "6min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

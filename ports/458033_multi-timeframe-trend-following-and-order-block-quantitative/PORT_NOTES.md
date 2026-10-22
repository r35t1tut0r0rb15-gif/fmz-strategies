# #458033 Multi Timeframe Trend Following and Order Block Quantitative Trading Strategy -> `fmz_458033_sma14_cross_order_block_1h_ema_trend_reversal`

- FMZ source id: 458033 (lineage).
- Source: https://www.fmz.com/strategy/458033 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 13:57:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C199). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the 1-hour EMAs end with the chart bar; the bracket as fixed fractions |
| 2 | PASS | SMA crossings against a range block with an EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `tp_frac` [0.0008955, 0.01] x `sl_frac` [0.0004477, 0.005]: **8 trials**; the 1-hour EMA 50 / 200 fixed.

## Ambiguities resolved

- Lower-time-frame EMAs from the last 1-hour bar. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`coarse_bar_stop`

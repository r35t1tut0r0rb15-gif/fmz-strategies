# #483055 多指标交叉动量趋势跟踪策略基于Supertrend与ADX双重确认的量化交易系统-Multi-Indicator-Momentum-Trend-Following-Strategy-Quantitative-Trading-System-Based-on-Supertrend-and-ADX-Dual-Confirmation -> `fmz_483055_supertrend3_14_up_adx14_rsi_outside_40_60_long`

- FMZ source id: 483055 (lineage).
- Source: https://www.fmz.com/strategy/483055 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:07:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C255). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend direction with ADX / RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`supertrend_factor` [3.0, 2.0] x `supertrend_period` [14, 10]: **4 trials**; DMI 14 / 14, ADX over 14, RSI 14.

## Ambiguities resolved

- Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

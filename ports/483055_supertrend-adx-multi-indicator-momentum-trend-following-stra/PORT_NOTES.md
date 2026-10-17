# #483055 多指标交叉动量趋势跟踪策略基于Supertrend与ADX双重确认的量化交易系统-Multi-Indicator-Momentum-Trend-Following-Strategy-Quantitative-Trading-System-Based-on-Supertrend-and-ADX-Dual-Confirmation -> `fmz_483055_supertrend_up_adx_rsi_long`

- FMZ source id: 483055 (lineage).
- Source: https://www.fmz.com/strategy/483055 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:07:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Supertrend (ATR bands), ADX and RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `adx_min` [14.0, 25.0]: **4 trials**; defaults 3 / 14 (the source's); Supertrend 14, DMI
14 / 14 and RSI 14 fixed.

## Ambiguities resolved

- `ta.supertrend` as TradingView documents it (direction -1 = up-trend); ADX as `ta.dmi` (as #426579).
- Every bar in the condition is an entry signal. Long only: opposite entries cannot occur. No stops. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

# #434715 基于指数移动平均线和MACD指标的量化交易策略Strategy-Based-on-Exponential-Moving-Average-and-MACD-Indicator -> `fmz_434715_impulse_macd_ema200_bracket`

- FMZ source id: 434715 (lineage).
- Source: https://www.fmz.com/strategy/434715 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-08 17:04:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; re-issued levels fixed at entry (approximation stated) |
| 2 | PASS | An impulse MACD, an average side and swing exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_ma` [34, 20] x `rr` [1.5, 3.0]: **4 trials**; EMA 200, signal 9 and the 20-bar stop look back fixed.

## Ambiguities resolved

- Re-issued levels fixed at the signal bar (trailing_stop_pending). Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`

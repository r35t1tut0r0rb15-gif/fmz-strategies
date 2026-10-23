# #488862 多指标融合期权销售策略趋势确认与ATR动态止损优化Multi-Indicator-Fusion-Options-Selling-Strategy-Trend-Confirmation-with-ATR-Dynamic-Stop-Loss-Optimization -> `fmz_488862_ema20_50_cross_adx_rsi_vwap_rolling_atr_stop_1h_reversal`

- FMZ source id: 488862 (lineage).
- Source: https://www.fmz.com/strategy/488862 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-31 13:10:34). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar re-sent stop followed in the signals |
| 2 | PASS | EMA crossings with ADX, RSI and VWAP filters |
| 3 | PASS | Exchange pair in the header only (option spreads named in the ids). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 2.5] x `adx_min` [15.0, 25.0]: **4 trials**; EMA 20 / 50, RSI 14, ATR 14.

## Ambiguities resolved

- Rolling stop followed at the next open. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

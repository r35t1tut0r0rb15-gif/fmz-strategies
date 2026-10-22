# #458134 多周期确认的移动平均线与RSI趋势交易策略-Multi-Timeframe-Moving-Average-and-RSI-Trend-Trading-Strategy -> `fmz_458134_sma9_21_rsi_1h_and_chart_agreement_atr_bracket_reversal`

- FMZ source id: 458134 (lineage).
- Source: https://www.fmz.com/strategy/458134 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 10:59:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 1-hour values from completed hours; ATR bracket at entry |
| 2 | PASS | SMA and RSI agreement on two timeframes with an ATR bracket |
| 3 | PASS | No exchange header (SOL named in the title only). |
| 4 | DONE | ATR-risk position size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `long_len` [21, 50] x `sl_atr` [1.5, 3.0]: **8 trials**; the target 3 ATR and the RSI levels fixed.

## Ambiguities resolved

- No bar size in the source (bar_size_pending); 1-hour values from the last completed hour; opening bracket kept (trailing_stop_pending). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`bar_size_pending, trailing_stop_pending`

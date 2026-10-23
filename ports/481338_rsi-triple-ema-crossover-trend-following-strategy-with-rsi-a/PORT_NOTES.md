# #481338 三均线交叉趋势跟踪策略结合RSI和成交量确认系统-Triple-EMA-Crossover-Trend-Following-Strategy-with-RSI-and-Volume-Confirmation-System -> `fmz_481338_ema50_200_cross_rsi_volume_rolling_atr_bracket_1h_long_only`

- FMZ source id: 481338 (lineage).
- Source: https://www.fmz.com/strategy/481338 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-10 14:16:32). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar re-sent bracket followed in the signals |
| 2 | PASS | EMA 50 / 200 crossings with RSI and volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.5, 2.5] x `rr` [3.0, 2.0]: **4 trials**; EMA 50 / 200, RSI 14, volume x 1.5.

## Ambiguities resolved

- Re-sent bracket followed at the next open. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

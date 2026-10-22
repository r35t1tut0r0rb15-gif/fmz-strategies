# #449851 EMA与RSI-MACD-ATR结合的双均线交叉策略-Enhanced-EMA-Crossover-Strategy-with-RSI-MACD-ATR -> `fmz_449851_ema8_14_cross_rsi_macd_atr_rise_point_bracket_reversal`

- FMZ source id: 449851 (lineage).
- Source: https://www.fmz.com/strategy/449851 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-29 17:33:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (re-sent levels marked) |
| 2 | PASS | EMA crossings with RSI, MACD and volatility filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_frac` [0.00238, 0.01] x `atr_rise` [1.1, 1.0]: **4 trials**; the 2 : 1 target ratio and the indicator lengths fixed.

## Ambiguities resolved

- Points as fractions of 42000; repeat-signal moves not followed. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

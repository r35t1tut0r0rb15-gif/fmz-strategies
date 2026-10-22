# #457777 4小时时间框架上的吞没形态交易策略与动态止盈止损优化-4-Hour-Timeframe-Engulfing-Pattern-Trading-Strategy-with-Dynamic-Take-Profit-and-Stop-Loss-Optimization -> `fmz_457777_engulfing_body_target_tick_stop_reversal`

- FMZ source id: 457777 (lineage).
- Source: https://www.fmz.com/strategy/457777 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-26 15:06:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the body target and tick stop as fractions; re-issued levels pending (mark) |
| 2 | PASS | Engulfing candles with a body target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_mult` [1.0, 2.0] x `sl_atr` [0.01, 1.0]: **4 trials**.

## Ambiguities resolved

- Tick stop as an ATR multiple (1D ~1000); re-issued levels pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

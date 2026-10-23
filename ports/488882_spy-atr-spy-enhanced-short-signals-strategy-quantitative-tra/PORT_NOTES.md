# #488882 SPY增强型空头信号策略-基于动态ATR目标优化的量化交易系统-SPY-Enhanced-Short-Signals-Strategy-Quantitative-Trading-System-with-Dynamic-ATR-Target-Optimization -> `fmz_488882_resistance_short_rsi_macd_volume_late_atr_bracket_1h_short_only`

- FMZ source id: 488882 (lineage).
- Source: https://www.fmz.com/strategy/488882 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 15:40:06). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; position-price bracket followed in the signals |
| 2 | PASS | Failed tests of the 20-bar high on volume with bearish momentum |
| 3 | PASS | Exchange pair in the header only (SPY named in the title). |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [1.5, 2.5] x `sl_atr` [1.0, 1.5]: **4 trials**; lookback 20, RSI 20 < 45, volume x 1.5.

## Ambiguities resolved

- Bracket armed only by repeated signals, followed at the next open. Volume = broker tick volume. Short only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "resistance_fade"`.

## Marks

`trailing_stop_pending`

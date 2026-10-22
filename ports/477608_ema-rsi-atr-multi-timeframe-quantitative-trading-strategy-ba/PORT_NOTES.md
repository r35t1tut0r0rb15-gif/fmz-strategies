# #477608 基于EMA平滑RSI和ATR动态止盈止损的多时序量化交易策略-Multi-Timeframe-Quantitative-Trading-Strategy-Based-on-EMA-Smoothed-RSI-and-ATR-Dynamic-Stop-Loss-Take-Profit -> `fmz_477608_ema_smoothed_rsi14_level_cross_atr_bracket_reversal`

- FMZ source id: 477608 (lineage).
- Source: https://www.fmz.com/strategy/477608 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 16:43:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C236). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | Smoothed RSI level crossings with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR multiplier stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`smoothing` [14, 5] x `atr_mult` [1.0, 2.0]: **4 trials**; RSI 14, levels 30 / 70.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

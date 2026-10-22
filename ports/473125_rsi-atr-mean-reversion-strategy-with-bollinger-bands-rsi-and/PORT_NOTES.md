# #473125 均值回归型布林带RSI策略结合ATR动态止损优化系统-Mean-Reversion-Strategy-with-Bollinger-Bands-RSI-and-ATR-Based-Dynamic-Stop-Loss-System -> `fmz_473125_bb20_rsi_extreme_mean_exit_atr_bracket_reversal`

- FMZ source id: 473125 (lineage).
- Source: https://www.fmz.com/strategy/473125 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-27 14:28:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C213). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR levels from the fill |
| 2 | PASS | Band and RSI extremes with mean exits and an ATR bracket |
| 3 | PASS | Exchange pair in the header only (SOL named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `std_dev` [2.0, 2.5] x `sl_atr` [2.0, 1.0]: **8 trials**; the 3 ATR target fixed.

## Ambiguities resolved

- ATR of the bar before the fill; per-bar ATR movement pending. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`

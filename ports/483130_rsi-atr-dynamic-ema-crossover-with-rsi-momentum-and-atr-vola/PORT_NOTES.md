# #483130 动态均线交叉结合RSI动量和ATR波动率的多层级确认交易策略-Dynamic-EMA-Crossover-with-RSI-Momentum-and-ATR-Volatility-Multi-Level-Confirmation-Trading-Strategy -> `fmz_483130_ema9_21_cross_rsi_atr1_5_3_bracket_reversal`

- FMZ source id: 483130 (lineage).
- Source: https://www.fmz.com/strategy/483130 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:53:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C258). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast_length` [9, 5] x `ema_slow_length` [21, 50]: **4 trials**; RSI 14, ATR 14, stop 1.5 ATR, target 3 ATR.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

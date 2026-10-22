# #482816 动态自适应多指标交叉策略结合SRSI和MACD的智能风控系统-Dynamic-Adaptive-Multi-Indicator-Crossing-Strategy-with-SRSI-MACD-Smart-Risk-Control-System -> `fmz_482816_stochrsi16_macd_scaled_turn_atr2_5_bracket_long`

- FMZ source id: 482816 (lineage).
- Source: https://www.fmz.com/strategy/482816 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:44:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Stochastic RSI turns with a scaled MACD |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`risk_factor` [2.5, 1.5] x `rsi_length` [16, 10]: **4 trials**; Stochastic 16, K 3, D 3, MACD 12 / 26 / 9, ATR 14.

## Ambiguities resolved

- The bracket re-sent each bar with the current ATR is fixed at the signal bar's ATR, active from the fill bar; pending.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

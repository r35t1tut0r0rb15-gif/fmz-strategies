# #484109 Dynamic Risk Managed Rapid SMA Crossover Momentum Capture Strategy -> `fmz_484109_macd5_13_3_rsi10_sma5_20_stack_state_atr_bracket_reversal`

- FMZ source id: 484109 (lineage).
- Source: https://www.fmz.com/strategy/484109 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 10:29:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | MACD / RSI / SMA stack states with an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity and 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_multiplier` [1.2, 2.0] x `take_profit_multiplier` [2.5, 4.0]: **4 trials**; SMA 5 / 20, RSI 10, MACD 5 / 13 / 3, ATR 10.

## Ambiguities resolved

- Repeat state signals re-send the bracket; pending. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

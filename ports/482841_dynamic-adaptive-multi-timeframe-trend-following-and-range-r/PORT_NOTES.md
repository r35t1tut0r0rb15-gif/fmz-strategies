# #482841 Dynamic Adaptive Multi Timeframe Trend Following and Range Reversal Hybrid Strategy -> `fmz_482841_ichimoku_regime_macd_rsi_stoch_atr2_stop_reversal`

- FMZ source id: 482841 (lineage).
- Source: https://www.fmz.com/strategy/482841 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-20 14:48:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C251). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR stop as a fraction of the fill |
| 2 | PASS | Ichimoku regime with MACD / RSI / Stochastic filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.0, 3.0] x `conversion_length` [9, 7]: **4 trials**; base 26, span B 52, MACD 12 / 26 / 9, RSI 14, Stochastic 14 / 3 / 3, ATR 14.

## Ambiguities resolved

- Spans undisplaced, as written. The stop re-sent by repeat signals is pending; the opening one is ported.
- MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

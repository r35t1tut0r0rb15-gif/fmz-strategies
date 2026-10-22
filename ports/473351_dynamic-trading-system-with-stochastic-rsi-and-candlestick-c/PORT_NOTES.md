# #473351 Dynamic Trading System with Stochastic RSI and Candlestick Confirmation -> `fmz_473351_stochrsi_k_20_80_cross_candle_reversal`

- FMZ source id: 473351 (lineage).
- Source: https://www.fmz.com/strategy/473351 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 14:58:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI level crossings with candle filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`oversold` [20, 30] x `overbought` [80, 70]: **4 trials**; the lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`

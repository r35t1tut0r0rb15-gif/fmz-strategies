# #442838 StochRSI反转交易策略StochRSI-Reversal-Trading-Strategy -> `fmz_442838_stoch_rsi_extreme_cross_reversal`

- FMZ source id: 442838 (lineage).
- Source: https://www.fmz.com/strategy/442838 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-26 14:17:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_length` [14, 7] x `oversold` [20, 10]: **4 trials** (overbought = 100 - oversold); the RSI length and smoothing fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

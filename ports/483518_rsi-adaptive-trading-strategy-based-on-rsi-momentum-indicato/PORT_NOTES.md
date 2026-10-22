# #483518 基于RSI动量指标的自适应交易策略-Adaptive-Trading-Strategy-Based-on-RSI-Momentum-Indicator -> `fmz_483518_rsi14_30_70_state_reversal`

- FMZ source id: 483518 (lineage).
- Source: https://www.fmz.com/strategy/483518 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:47:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C259). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent close bracket pending |
| 2 | PASS | RSI extreme states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period` [14, 7] x `rsi_oversold` [30.0, 20.0]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- The bracket re-sent from each bar's close is pending, not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`

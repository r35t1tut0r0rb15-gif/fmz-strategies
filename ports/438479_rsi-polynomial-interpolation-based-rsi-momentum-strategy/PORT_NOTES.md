# #438479 基于多项式插值的RSI动量指标策略Polynomial-Interpolation-Based-RSI-Momentum-Strategy -> `fmz_438479_delta_rsi_polynomial_slope_signal_cross_1h_reversal`

- FMZ source id: 438479 (lineage).
- Source: https://www.fmz.com/strategy/438479 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 13:46:53). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed RSI derivative against its signal line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [50, 30] x `signal_len` [9, 5]: **4 trials**; polynomial order 3, RSI 21.

## Ambiguities resolved

- endshort reuses the long-exit signal (sic); entries reverse. Volume filter off: volume not used. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

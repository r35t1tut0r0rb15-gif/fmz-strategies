# #439876 RSI与布林带支撑阻力动态结合量化策略RSI-Combined-with-Bollinger-Bands-and-Dynamic-Support-Resistance-Quantitative-Strategy -> `fmz_439876_rsi14_extreme_exit_crossings`

- FMZ source id: 439876 (lineage).
- Source: https://www.fmz.com/strategy/439876 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-24 15:19:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `oversold` [30, 20]: **4 trials**; overbought = 100 - oversold.

## Ambiguities resolved

- S/R and range tests filter nothing, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

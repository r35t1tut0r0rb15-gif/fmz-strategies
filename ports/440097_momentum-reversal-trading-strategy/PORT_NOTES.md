# #440097 Momentum Reversal Trading Strategy -> `fmz_440097_rsi14_30_70_exit_cross_daily`

- FMZ source id: 440097 (lineage).
- Source: https://www.fmz.com/strategy/440097 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 15:51:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

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

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

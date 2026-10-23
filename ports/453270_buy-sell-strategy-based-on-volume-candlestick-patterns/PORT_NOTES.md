# #453270 Buy Sell Strategy Based on Volume Candlestick Patterns -> `fmz_453270_sma60_vs_switching_ema_accuracy_cross_reversal`

- FMZ source id: 453270 (lineage).
- Source: https://www.fmz.com/strategy/453270 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-03 16:31:28). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA 60 crossings of a switching EMA line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_sma` [60, 100] x `slow` [30, 50]: **4 trials**; fast EMA 10.

## Ambiguities resolved

- Closes never act (wrong ids). Volume not used. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

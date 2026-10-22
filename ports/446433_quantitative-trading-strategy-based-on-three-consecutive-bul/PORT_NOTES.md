# #446433 Quantitative Trading Strategy Based on Three Consecutive Bullish Bearish Candles and Dual Moving Averages -> `fmz_446433_three_growing_bodies_reversal`

- FMZ source id: 446433 (lineage).
- Source: https://www.fmz.com/strategy/446433 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-28 16:22:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Growing candle bodies |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

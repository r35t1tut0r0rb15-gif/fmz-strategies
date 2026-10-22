# #476280 Cloud Based Bollinger Bands Double Moving Average Quantitative Trend Strategy -> `fmz_476280_ichimoku_span_ab_cross_reversal`

- FMZ source id: 476280 (lineage).
- Source: https://www.fmz.com/strategy/476280 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-27 15:54:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku span crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 20] x `span_b` [52, 120]: **4 trials**; base 26.

## Ambiguities resolved

- Spans read undisplaced, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

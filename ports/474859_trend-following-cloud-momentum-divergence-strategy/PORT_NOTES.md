# #474859 Trend Following Cloud Momentum Divergence Strategy -> `fmz_474859_macd_cross_beyond_spans_rsi_reversal`

- FMZ source id: 474859 (lineage).
- Source: https://www.fmz.com/strategy/474859 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 15:51:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C225). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings beyond the spans with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and levels are constants).

## Ambiguities resolved

- Spans undisplaced in the tests, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

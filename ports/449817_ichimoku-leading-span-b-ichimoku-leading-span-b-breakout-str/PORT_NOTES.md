# #449817 Ichimoku-Leading-Span-B-突破策略-Ichimoku-Leading-Span-B-Breakout-Strategy -> `fmz_449817_displaced_span_b_cross_long`

- FMZ source id: 449817 (lineage).
- Source: https://www.fmz.com/strategy/449817 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-29 14:45:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the span from 26 bars back |
| 2 | PASS | Displaced Span B crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`span_b` [52, 26] x `displacement` [26, 13]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

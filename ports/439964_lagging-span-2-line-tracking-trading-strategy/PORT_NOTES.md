# #439964 Lagging Span 2 Line Tracking Trading Strategy -> `fmz_439964_span_b_displaced_cross_tick_bracket`

- FMZ source id: 439964 (lineage).
- Source: https://www.fmz.com/strategy/439964 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 13:00:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick brackets -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k` [1.0, 0.5] x `span_len` [52, 26]: **4 trials**; k scales the three ATR multiples 3.33 / 6.67 / 2.5.

## Ambiguities resolved

- Tick brackets as ATR multiples. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

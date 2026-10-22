# #458269 Ichimoku Kinko Hyo Trend Following and Support Resistance Strategy -> `fmz_458269_close_vs_span_b_mid52_state_reversal`

- FMZ source id: 458269 (lineage).
- Source: https://www.fmz.com/strategy/458269 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:25:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs the 52-bar mid line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`span_b` [52, 26]: **2 trials**.

## Ambiguities resolved

- Span B undisplaced (as written). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

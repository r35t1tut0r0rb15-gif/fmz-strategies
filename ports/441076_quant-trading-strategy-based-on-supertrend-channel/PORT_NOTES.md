# #441076 Quant Trading Strategy Based on SuperTrend Channel -> `fmz_441076_atr_stops_supertrend_7x7_flip_reversal`

- FMZ source id: 441076 (lineage).
- Source: https://www.fmz.com/strategy/441076 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 13:57:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C145). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend direction flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [7, 14] x `mult` [7.0, 3.0]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

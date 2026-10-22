# #442257 Breakthrough Fair Value Gap Strategy -> `fmz_442257_fair_value_gap_reversal`

- FMZ source id: 442257 (lineage).
- Source: https://www.fmz.com/strategy/442257 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 15:47:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three-bar gap tests |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gap_back` [2, 3]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

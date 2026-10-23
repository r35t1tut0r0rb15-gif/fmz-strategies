# #430014 Moving Average Tracking Stop Loss Strategy -> `fmz_430014_most_ehma28_pct38_line_cross_reversal`

- FMZ source id: 430014 (lineage).
- Source: https://www.fmz.com/strategy/430014 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-24 11:21:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MOST trailing line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, pyramiding 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`yuzde` [3.8, 2.0] x `length` [28, 14]: **4 trials**.

## Ambiguities resolved

- HulleMA default (no volume). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`

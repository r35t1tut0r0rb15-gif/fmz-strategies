# #442381 Dynamic Position Sizing Quant Strategy -> `fmz_442381_sma14_28_cross_reversal`

- FMZ source id: 442381 (lineage).
- Source: https://www.fmz.com/strategy/442381 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 14:52:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C155). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The compounding quantity rule and position cap stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 9] x `slow` [28, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

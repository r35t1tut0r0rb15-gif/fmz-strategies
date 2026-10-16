# #429388 Ichimoku Cloud Day Trading Strategy -> `fmz_429388_ichimoku_sar_filter`

- FMZ source id: 429388 (lineage).
- Source: https://www.fmz.com/strategy/429388 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-16 16:10:55). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the SAR trailing stop is not emitted (rule 2). |
| 2 | PASS | Price vs lines from the bars only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 3 stored; the SAR stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`base` [26, 52] x `sar_max` [0.2, 0.1]: **4 trials**; conversion 9, span 2 52, displacement 26, SAR start / step 0.02 fixed.

## Ambiguities resolved

- Pending (not emitted): while long, a sell stop at the bar's parabolic SAR (0.02 / 0.02 / 0.2),
  re-issued each bar; while short, a buy stop at the SAR.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`trailing_stop_pending`

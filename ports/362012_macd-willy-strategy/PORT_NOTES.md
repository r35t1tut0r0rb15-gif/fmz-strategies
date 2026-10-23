# #362012 MACD Willy Strategy -> `fmz_362012_ema200_macd_hist_smoothed_wpr_state_reversal`

- FMZ source id: 362012 (lineage).
- Source: https://www.fmz.com/strategy/362012 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 16:32:15). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA side with MACD and smoothed %R states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital 10000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emalen1` [200, 100] x `w_length` [34, 14]: **4 trials**; MACD 12 / 26 / 9, WMA 5, EMA 13.

## Ambiguities resolved

- The volume average is unused (volume not used). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

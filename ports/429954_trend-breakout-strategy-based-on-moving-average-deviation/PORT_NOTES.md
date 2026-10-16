# #429954 Trend Breakout Strategy Based on Moving Average Deviation -> `fmz_429954_wma_zscore_turn_long`

- FMZ source id: 429954 (lineage).
- Source: https://www.fmz.com/strategy/429954 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-23 15:38:37). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A z-score only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The repeated adds stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [17, 34] x `band` [1.0, 1.5]: **4 trials**; WMA 3 of ohlc4 fixed.

## Ambiguities resolved

- Adds not ported. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`none`

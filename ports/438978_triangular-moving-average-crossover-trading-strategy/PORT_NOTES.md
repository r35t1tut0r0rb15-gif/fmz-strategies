# #438978 Triangular Moving Average Crossover Trading Strategy -> `fmz_438978_kozlod_three_ma_cross`

- FMZ source id: 438978 (lineage).
- Source: https://www.fmz.com/strategy/438978 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-16 18:18:02). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crossings with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the off SL / PT inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_type` ["SMA", "EMA"] x `short_len` [5, 10]: **4 trials**; medium 20 and long 100 fixed; SL / PT off.

## Ambiguities resolved

- SL / PT off. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

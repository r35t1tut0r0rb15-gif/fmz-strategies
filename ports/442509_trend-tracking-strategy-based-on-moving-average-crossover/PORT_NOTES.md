# #442509 Trend Tracking Strategy Based on Moving Average Crossover -> `fmz_442509_six_sma_cross_named_ids_reversal`

- FMZ source id: 442509 (lineage).
- Source: https://www.fmz.com/strategy/442509 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 14:02:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [200, 100] x `short_slow` [20, 40]: **4 trials** (the SMA 200 of the first long id and the SMA 20 of the short entry); the other lengths fixed.

## Ambiguities resolved

- Named ids in call order, one position at a time; closes act only on their own id. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

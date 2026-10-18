# #435959 Multiple Moving Averages Crossover Trading Strategy -> `fmz_435959_triple_sma_cross_ids_long`

- FMZ source id: 435959 (lineage).
- Source: https://www.fmz.com/strategy/435959 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 14:12:20). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430849. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [50, 20] x `ma2` [100, 50]: **4 trials**; SMA 200 fixed.

## Ambiguities resolved

- Per-id closes; one long at a time; orders in call order. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

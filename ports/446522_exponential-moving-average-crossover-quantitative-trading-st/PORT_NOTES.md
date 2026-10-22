# #446522 Exponential Moving Average Crossover Quantitative Trading Strategy -> `fmz_446522_ema5_10_cross_at_10bar_extreme_from_flat`

- FMZ source id: 446522 (lineage).
- Source: https://www.fmz.com/strategy/446522 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 10:59:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings at close extremes, opposite-crossing exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 9] x `slow` [10, 21]: **4 trials**; the 10-bar look-back fixed.

## Ambiguities resolved

- Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

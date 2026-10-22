# #449954 Exponential Moving Average Crossover Leverage Strategy -> `fmz_449954_ema20_55_cross_long`

- FMZ source id: 449954 (lineage).
- Source: https://www.fmz.com/strategy/449954 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:26:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The leveraged quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [55, 100]: **4 trials**; the EMA mode fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

# #427257 TEMA Crossover Trading Strategy -> `fmz_427257_tema_cross`

- FMZ source id: 427257 (lineage).
- Source: https://www.fmz.com/strategy/427257 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-19 15:41:47). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [34, 55, 21] x `fast` [13, 8]: **6 trials**; defaults 34 / 13 (the source's).

## Ambiguities resolved

- `cross()` in either direction; the side follows which TEMA ends on top (slow below fast = long), as written.
- REVERSAL INTENDED. FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

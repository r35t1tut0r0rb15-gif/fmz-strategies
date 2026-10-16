# #429161 SuperTrend Strategy -> `fmz_429161_supertrend_long`

- FMZ source id: 429161 (lineage).
- Source: https://www.fmz.com/strategy/429161 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-13 17:03:55). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy() stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [22, 14] x `mult` [3.0, 2.0]: **4 trials**; Long Only fixed.

## Ambiguities resolved

- Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

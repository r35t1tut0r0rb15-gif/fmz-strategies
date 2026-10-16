# #428578 EMA Enhanced SuperTrend Strategy -> `fmz_428578_supertrend_flip_6h`

- FMZ source id: 428578 (lineage).
- Source: https://www.fmz.com/strategy/428578 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 10:07:15). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.
- Duplicate group: **DG428578** (4 members, best partner #428613, Jaccard 0.882), also in ND427399; ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR multiples only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG428578 / ND427399. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 14] x `multiplier` [3, 2]: **4 trials**; defaults 10 / 3 (the source's).

## Ambiguities resolved

- Wilder ATR (default switch on). The appended EMA 305 (second //@version=3 block) is drawn only. Date window open.
- REVERSAL INTENDED. FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

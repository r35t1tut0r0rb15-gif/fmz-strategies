# #427399 Long-Term Trading Strategy Based on SuperTrend -> `fmz_427399_supertrend_3d_long_term`

- FMZ source id: 427399 (lineage).
- Source: https://www.fmz.com/strategy/427399 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 17:14:33). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.
- Near-duplicate group: **ND427399** (3 members, best partner #428578, Jaccard 0.709); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR multiples, MA filter. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Cash qty 50000 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427399. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 20] x `multiplier` [3, 2] x `ma_period` [20, 50]: **8 trials**; defaults 10 / 3 / 20 (the source's).

## Ambiguities resolved

- 3-day bars as worker A's 2-day ports: blocks of three broker-day dates from 1970-01-01 (block phase: the same decision owed as for #426995).
- Wilder ATR (the "change ATR" switch is on). The date window is dropped.
- A long closes and a short opens on the down-turn (REVERSAL INTENDED). FREQ = "3D".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

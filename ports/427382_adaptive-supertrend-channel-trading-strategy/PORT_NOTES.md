# #427382 Adaptive Supertrend Channel Trading Strategy -> `fmz_427382_supertrend_cloud_long`

- FMZ source id: 427382 (lineage).
- Source: https://www.fmz.com/strategy/427382 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 15:17:51). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, initial capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multi` [3, 2] x `period` [10, 20] x `self_adjust` [False, True]: **8 trials**; defaults 3 / 10 / False (the source's).

## Ambiguities resolved

- The lines start from 0 with an explicit [1] (as written); trend starts at 1 (nz).
- time_cond is the constant true. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

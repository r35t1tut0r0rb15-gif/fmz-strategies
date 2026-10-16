# #430651 DEC策略Leledec-DEC-Strategy -> `fmz_430651_leledec_exhaustion`

- FMZ source id: 430651 (lineage).
- Source: https://www.fmz.com/strategy/430651 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-31 11:47:00). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Close counts and bar extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`maj_qual` [6, 9] x `maj_len` [30, 20]: **4 trials**; minor 5 / 5 and close look-back 4 fixed.

## Ambiguities resolved

- Buy on the major, sell on the minor exhaustion, as written. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "td_sequential"`.

## Marks

`none`

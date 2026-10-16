# #430590 Triple Moving Average Crossover Strategy -> `fmz_430590_williams_three_lines`

- FMZ source id: 430590 (lineage).
- Source: https://www.fmz.com/strategy/430590 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-30 16:38:01). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Displaced moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`l_length` [13, 21] x `l_offset` [8, 5]: **4 trials**; middle 8 / 5 and short 5 / 3 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "alligator"`.

## Marks

`none`

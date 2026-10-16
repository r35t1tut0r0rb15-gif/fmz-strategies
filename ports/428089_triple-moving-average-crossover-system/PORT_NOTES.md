# #428089 Triple Moving Average Crossover System -> `fmz_428089_three_sma_alternating`

- FMZ source id: 428089 (lineage).
- Source: https://www.fmz.com/strategy/428089 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 15:33:14). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

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

`length1` [18, 36] x `length3` [4, 2]: **4 trials**; defaults 18 / 4 (the source's); SMA 9 fixed.

## Ambiguities resolved

- The short entry needs an open long (as written): long-only start, then alternating. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

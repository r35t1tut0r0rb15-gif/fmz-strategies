# #436491 Three SMA Crossover Momentum Strategy -> `fmz_436491_three_sma_kama_alignment`

- FMZ source id: 436491 (lineage).
- Source: https://www.fmz.com/strategy/436491 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-25 12:06:36). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C90). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average alignment and adaptive average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND433101. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma1` [16, 12] x `kama_len` [50, 30]: **4 trials**; the other lengths fixed.

## Ambiguities resolved

- An efficiency ratio of exactly 0 gives power 1/0 and a zero smoothing (the KAMA holds). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`

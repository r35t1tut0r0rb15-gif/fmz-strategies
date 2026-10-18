# #436224 Broken High Low Strategy -> `fmz_436224_broken_candle_two_ids_long`

- FMZ source id: 436224 (lineage).
- Source: https://www.fmz.com/strategy/436224 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 12:59:43). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Both ids long; stacked trades held as one position |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [5, 8] x `slow_ma` [10, 20]: **4 trials**.

## Ambiguities resolved

- Both ids are long trades; one combined long position. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

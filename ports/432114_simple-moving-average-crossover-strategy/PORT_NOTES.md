# #432114 Simple Moving Average Crossover Strategy -> `fmz_432114_four_sma_cross`

- FMZ source id: 432114 (lineage).
- Source: https://www.fmz.com/strategy/432114 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-14 16:17:16). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [20, 10] x `len4` [200, 150]: **4 trials**; SMA 50 / 100 fixed.

## Ambiguities resolved

- "and" before "or" as in Pine. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

# #439621 Precise Trend Reversal Moving Average Crossover Strategy -> `fmz_439621_sma50_200_golden_death_cross`

- FMZ source id: 439621 (lineage).
- Source: https://www.fmz.com/strategy/439621 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 12:14:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

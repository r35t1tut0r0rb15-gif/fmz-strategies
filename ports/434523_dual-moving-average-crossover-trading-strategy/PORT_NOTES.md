# #434523 Dual Moving Average Crossover Trading Strategy -> `fmz_434523_three_ema_side`

- FMZ source id: 434523 (lineage).
- Source: https://www.fmz.com/strategy/434523 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-07 10:36:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price against averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 400]: **4 trials**; the EMA 144 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

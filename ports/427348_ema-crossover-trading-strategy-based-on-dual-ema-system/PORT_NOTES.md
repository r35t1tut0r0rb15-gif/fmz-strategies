# #427348 Crossover Trading Strategy Based on Dual EMA System -> `fmz_427348_cross_algo_ema_13_50`

- FMZ source id: 427348 (lineage).
- Source: https://www.fmz.com/strategy/427348 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 11:39:40). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

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

`short_len` [13, 8] x `long_len` [50, 26, 100]: **6 trials**; defaults 13 / 50 (the source's).

## Ambiguities resolved

- Each cross closes one side and opens the other on the same bar (REVERSAL INTENDED). FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

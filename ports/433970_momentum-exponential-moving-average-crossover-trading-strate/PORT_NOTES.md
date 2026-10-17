# #433970 Momentum Exponential Moving Average Crossover Trading Strategy -> `fmz_433970_ema_50_200_cross`

- FMZ source id: 433970 (lineage).
- Source: https://www.fmz.com/strategy/433970 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 18:21:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

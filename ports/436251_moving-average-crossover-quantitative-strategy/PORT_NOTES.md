# #436251 Moving Average Crossover Quantitative Strategy -> `fmz_436251_ema_filter_smoothed_offset`

- FMZ source id: 436251 (lineage).
- Source: https://www.fmz.com/strategy/436251 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 15:05:24). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C88). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit levels -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level_frac` [0.000125, 0.001] x `ema_length` [13, 21]: **4 trials**; the EMA 12 / 9 pair fixed.

## Ambiguities resolved

- Price-unit levels -> fractions; ternaries reduced. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

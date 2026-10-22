# #442256 Adaptive Moving Average Crossover System with Momentum Breakout -> `fmz_442256_yasin_zero_lag_tema_cross_reversal`

- FMZ source id: 442256 (lineage).
- Source: https://www.fmz.com/strategy/442256 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 15:43:46). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C153). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Zero-lag TEMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [55, 30]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

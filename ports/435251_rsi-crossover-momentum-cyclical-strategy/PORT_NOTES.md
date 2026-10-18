# #435251 RSI Crossover Momentum Cyclical Strategy -> `fmz_435251_rsi_60_80_cross_long`

- FMZ source id: 435251 (lineage).
- Source: https://www.fmz.com/strategy/435251 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 15:41:33). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_th` [60, 55] x `sell_th` [80, 70]: **4 trials**; RSI 14 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

# #436219 Quantitative Trading Price Breakthrough Strategy -> `fmz_436219_lows_based_filters`

- FMZ source id: 436219 (lineage).
- Source: https://www.fmz.com/strategy/436219 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-22 12:42:15). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Averages, a channel and an oscillator filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [25, 20] x `mult` [2.0, 1.5]: **4 trials**; EMA 200, MACD 4 / 34 / 5 and stochastic 10 fixed.

## Ambiguities resolved

- Everything on the low price; states every bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`

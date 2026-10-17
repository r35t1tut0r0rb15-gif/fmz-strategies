# #432356 Dual Moving Average Crossover Momentum Strategy -> `fmz_432356_macd_histogram_growth`

- FMZ source id: 432356 (lineage).
- Source: https://www.fmz.com/strategy/432356 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-16 17:25:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C52). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram sign and slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND364540. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 17]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- Same-timeframe security adds nothing. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`

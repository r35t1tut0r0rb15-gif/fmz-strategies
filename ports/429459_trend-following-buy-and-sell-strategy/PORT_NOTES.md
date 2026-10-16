# #429459 Trend Following Buy and Sell Strategy -> `fmz_429459_higher_high_long`

- FMZ source id: 429459 (lineage).
- Source: https://www.fmz.com/strategy/429459 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 12:59:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | High comparisons and indicator slopes only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_a` [20, 50] x `period_k` [5, 14]: **4 trials**; MACD 5 / 20 / 30 and the filters on fixed.

## Ambiguities resolved

- The month / year filter is dropped as a backtest window. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`

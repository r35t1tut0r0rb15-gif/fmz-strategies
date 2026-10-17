# #434966 Trend Trader Bands Backtest Strategy Based on Trend Trader Moving Average -> `fmz_434966_trend_trader_bands`

- FMZ source id: 434966 (lineage).
- Source: https://www.fmz.com/strategy/434966 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-11 13:12:44). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | The price-unit band step -> an ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG434966, ND434966. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [3.0, 2.0] x `step_atr` [0.02, 0.5]: **4 trials**; length 21 and MA 21 fixed.

## Ambiguities resolved

- Band step -> ATR multiple; ret seeded at 0. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`

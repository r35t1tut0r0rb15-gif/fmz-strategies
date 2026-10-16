# #427588 Trading Strategy Based on Faytterro Estimator -> `fmz_427588_faytterro_estimator`

- FMZ source id: 427588 (lineage).
- Source: https://www.fmz.com/strategy/427588 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-22 14:12:27). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the estimator uses past bars only. |
| 2 | ADAPT | 500 price-unit gaps -> `gap_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strong-entry width (units) stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `gap_atr` [0.5, 0.25, 1]: **6 trials**; defaults 10 / 0.5; look-back 100 fixed. 500 USD on daily BTC is about half an ATR (judgement, stated before any backtest).

## Ambiguities resolved

- `(close[barssince(buy or sell)])[1]` = the close at the last raw signal before the bar.
- The strong entries are a subset of the plain ones (more units): sizing. strategy() commented out: one position.
- REVERSAL INTENDED. Broker-day bars. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`

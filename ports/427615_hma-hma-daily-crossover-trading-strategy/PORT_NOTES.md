# #427615 HMA Daily Crossover Trading Strategy -> `fmz_427615_hma_daily_open_basket`

- FMZ source id: 427615 (lineage).
- Source: https://www.fmz.com/strategy/427615 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-22 17:07:15). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; open-profit check on bar closes. |
| 2 | ADAPT | 0.05 $ open-profit thresholds -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 28] x `tp_atr` [0.01, 0.5] x `sl_atr` [0.01, 0.5]: **8 trials**; defaults 14 / 0.01 / 0.01. The source's 0.05 $ on one hourly BTC contract is about 0.0003 ATR (judgement before any backtest).

## Ambiguities resolved

- strategy.order nets: an opposite order flattens; same-side adds are sizing.
- s2 = broker-day open, last completed day's on history; s2[1], s2[2] are hourly lags as written.
- Close-all is applied before the bar's new order (same-side re-entry keeps the position: stated approximation).
- FREQ = "1h". Close-checked exits (exit signals), no house stops.

## Decision owed

The dollar thresholds look written for a BTC-quoted account with a 1 % quantity (the commented strategy() line); the intended distances are unknown.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

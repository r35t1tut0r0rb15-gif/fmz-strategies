# #430065 Bull and Bear Power Backtest Strategy -> `fmz_430065_elder_bull_power_day_high`

- FMZ source id: 430065 (lineage).
- Source: https://www.fmz.com/strategy/430065 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-24 16:43:52). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A price minus its moving average, compared with zero. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430065. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [13, 8, 26]: **3 trials**; trigger 0 fixed.

## Ambiguities resolved

- Day boundary = broker day (17:00 America/New_York). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`

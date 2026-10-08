# #426829 K Moving Average Candle Regression Strategy -> `fmz_426829_ma_candle_linreg_long`

- Source: https://www.fmz.com/strategy/426829 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 17:50:14). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`loopback` [30, 60] x `m_length` [10, 20] x `st_length` [100, 200]: **8 trials**, defaults 60 / 20 / 200 (the source's); lookback 40, 0.85 / 1.01, BB 3 fixed; aggressive on, VixFix off.

## Ambiguities resolved

- na comparisons are false: while val is na the colour is orange (as Pine).
- Same bar: from flat the entry stands; while long the exit goes flat. Pine population stdev.
- Long only. FREQ = "15min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`

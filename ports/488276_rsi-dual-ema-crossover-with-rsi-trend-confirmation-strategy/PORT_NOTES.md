# #488276 双指数移动平均线交叉与RSI趋势确认策略-Dual-EMA-Crossover-with-RSI-Trend-Confirmation-Strategy -> `fmz_488276_ema9_21_cross_rsi30`

- FMZ source id: 488276 (lineage).
- Source: https://www.fmz.com/strategy/488276 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 14:44:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMAs and an oscillator. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_slow` [21, 30] x `rsi_level` [30, 40]: **4 trials**; defaults 21 / 30 (the source's); EMA 9 and RSI 14 fixed.

## Ambiguities resolved

- Closes act on the position at the bar's start (#430850); a short signal while long reverses. As written a short
  closes on the first bar with RSI back above 30. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

# #434687 Trend and Moving Average Crossover Based Multi Functional Algorithmic Trading Strategy -> `fmz_434687_ut_bot_ema_spread`

- FMZ source id: 434687 (lineage).
- Source: https://www.fmz.com/strategy/434687 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-08 12:14:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C70). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit spread levels -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [3.0, 1.5] x `lvl_scale` [1.0, 20.0]: **4 trials**; `lvl_scale` multiplies both ATR levels (0.025 / 0.075); ATR 10, EMA 26 / 50 fixed.

## Ambiguities resolved

- UT Bot line as a close-based signal; spread levels -> ATR multiples. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`

# #451713 超级均线与Upperband交叉策略-Super-Moving-Average-and-Upperband-Crossover-Strategy -> `fmz_451713_range_scaled_upperband_breakout_ema3_exit_long`

- FMZ source id: 451713 (lineage).
- Source: https://www.fmz.com/strategy/451713 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 13:50:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Breakouts over a range-scaled band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [0.001, 0.0005] x `length` [20, 50]: **4 trials**; the EMA 3 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`

# #439823 久期均线交叉Renko策略Long-term-Moving-Average-Crossover-Renko-Strategy -> `fmz_439823_tema5_sma3_cross_min_gain_exit_long`

- FMZ source id: 439823 (lineage).
- Source: https://www.fmz.com/strategy/439823 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-24 10:55:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TEMA / SMA crossings and a gain test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427372. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`min_gain` [2.0, 0.0] x `smma_length` [30, 60]: **4 trials**; TEMA 5 and SMA 3 fixed.

## Ambiguities resolved

- Gain-gated close on the fill price. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

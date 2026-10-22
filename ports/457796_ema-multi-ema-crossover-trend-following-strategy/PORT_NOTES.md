# #457796 多重EMA交叉趋势跟踪策略Multi-EMA-Crossover-Trend-Following-Strategy -> `fmz_457796_ema21_55_and_55_200_cross_reversal`

- FMZ source id: 457796 (lineage).
- Source: https://www.fmz.com/strategy/457796 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-26 16:24:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Two EMA crossing pairs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 9] x `mid` [55, 50] x `slow` [200, 100]: **8 trials**.

## Ambiguities resolved

- Later call wins a two-way bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

# #442939 基于MACD与RSI结合的交叉策略MACD-Crossover-Strategy-with-RSI-Confirmation -> `fmz_442939_macd_cross_rsi50_latch_three_bar_exit`

- FMZ source id: 442939 (lineage).
- Source: https://www.fmz.com/strategy/442939 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 15:07:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings with latched RSI flags; bar-count exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`exit_after_bars` [3, 6] x `fast_length` [12, 8]: **4 trials**; the slow and signal lengths and the RSI fixed.

## Ambiguities resolved

- Latched RSI flags as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`

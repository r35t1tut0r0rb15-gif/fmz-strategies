# #442967 动量均线交叉EMA九股MACD策略Momentum-Line-Crossover-EMA-Nine-Stock-MACD-Strategy -> `fmz_442967_ema9_30_cross_rising_deviation_reversal`

- FMZ source id: 442967 (lineage).
- Source: https://www.fmz.com/strategy/442967 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 16:49:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C164). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a volatility filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [30, 50]: **4 trials**; the deviation length fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

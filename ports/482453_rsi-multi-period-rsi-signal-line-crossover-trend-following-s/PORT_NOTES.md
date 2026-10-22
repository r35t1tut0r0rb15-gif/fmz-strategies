# #482453 基于RSI信号线交叉的多周期趋势跟踪交易策略-Multi-Period-RSI-Signal-Line-Crossover-Trend-Following-Strategy -> `fmz_482453_ultimate_rsi14_signal_cross_reversal`

- FMZ source id: 482453 (lineage).
- Source: https://www.fmz.com/strategy/482453 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:04:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C244). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Augmented RSI signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `smooth` [14, 7]: **4 trials**; RMA, signal EMA.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

# #482453 基于RSI信号线交叉的多周期趋势跟踪交易策略-Multi-Period-RSI-Signal-Line-Crossover-Trend-Following-Strategy -> `fmz_482453_ultimate_rsi_signal_cross_always_in`

- FMZ source id: 482453 (lineage).
- Source: https://www.fmz.com/strategy/482453 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:04:49). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An RSI variant and its signal line. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 28] x `smooth` [14, 7]: **4 trials**; defaults 14 / 14 (the source's); RMA and EMA methods fixed.

## Ambiguities resolved

- The range test checks a rising upper extreme first, then a falling lower one, else the close change (as written).
- The closes repeat the reversal. REVERSAL INTENDED (always in). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

none

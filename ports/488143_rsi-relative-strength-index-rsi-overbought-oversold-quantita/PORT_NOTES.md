# #488143 相对强弱指标RSI超买超卖量化交易策略-Relative-Strength-Index-RSI-Overbought-Oversold-Quantitative-Trading-Strategy -> `fmz_488143_rsi14_30_70_cross_entries_exits_reversal`

- FMZ source id: 488143 (lineage).
- Source: https://www.fmz.com/strategy/488143 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-25 14:22:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI threshold crossings |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 5 % of equity and the alert lot size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`oversold` [30, 20] x `overbought` [70, 80]: **4 trials**; RSI 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`

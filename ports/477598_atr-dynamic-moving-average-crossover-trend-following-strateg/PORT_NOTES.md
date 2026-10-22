# #477598 动态均线交叉趋势跟踪策略结合ATR风险管理系统-Dynamic-Moving-Average-Crossover-Trend-Following-Strategy-with-ATR-Risk-Management-System -> `fmz_477598_sma10_50_cross_atr15_bracket_reversal`

- FMZ source id: 477598 (lineage).
- Source: https://www.fmz.com/strategy/477598 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:27:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | SMA crossings with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 200 % / close stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.5, 3.0] x `slow` [50, 100]: **4 trials**; SMA 10, ATR 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

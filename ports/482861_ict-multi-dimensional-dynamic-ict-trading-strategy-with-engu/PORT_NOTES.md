# #482861 多维度动态ICT交易策略结合吞没形态与供需区域分析系统-Multi-Dimensional-Dynamic-ICT-Trading-Strategy-with-Engulfing-Patterns-and-Supply-Demand-Zone-Analysis-System -> `fmz_482861_engulfing_20bar_zone_1_5_3pct_bracket_reversal`

- FMZ source id: 482861 (lineage).
- Source: https://www.fmz.com/strategy/482861 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:44:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | Engulfing candles with 20-bar extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_perc` [1.5, 1.0] x `take_profit_perc` [3.0, 2.0]: **4 trials**; zones over 20 bars.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`

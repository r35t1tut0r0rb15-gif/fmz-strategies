# #488537 Vishal-自适应多指标交易策略-Vishal-Adaptive-Multi-Indicator-Trading-Strategy -> `fmz_488537_macd_sar_supertrend_flags_sar_exit_reversal`

- FMZ source id: 488537 (lineage).
- Source: https://www.fmz.com/strategy/488537 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:17:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD / SAR / SuperTrend agreement with a SAR exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Strategy(): capital 100000, 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atrPeriod` [11, 20]: **4 trials**; MACD 13 / 27 / 9, SAR 0.02 / 0.2.

## Ambiguities resolved

- The kept flags are followed in a loop. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

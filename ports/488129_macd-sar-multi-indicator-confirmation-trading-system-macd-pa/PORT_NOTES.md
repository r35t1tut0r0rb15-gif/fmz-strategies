# #488129 多指标协同确认交易策略MACD抛物线SAR与超级趋势三重验证系统-Multi-Indicator-Confirmation-Trading-System-MACD-Parabolic-SAR-and-Supertrend-Triple-Verification-Framework -> `fmz_488129_supertrend3_10_sar_macd_agreement_reversal`

- FMZ source id: 488129 (lineage).
- Source: https://www.fmz.com/strategy/488129 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-25 11:51:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend / SAR / MACD agreement |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, no commission or slippage, stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrFactor` [3.0, 2.0] x `atrPeriod` [10, 20]: **4 trials**; SAR 0.02 / 0.2, MACD 12 / 26 / 9.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

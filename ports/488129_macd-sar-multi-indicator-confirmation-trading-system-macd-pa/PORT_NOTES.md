# #488129 多指标协同确认交易策略MACD抛物线SAR与超级趋势三重验证系统-Multi-Indicator-Confirmation-Trading-System-MACD-Parabolic-SAR-and-Supertrend-Triple-Verification-Framework -> `fmz_488129_macd_sar_supertrend_triple`

- FMZ source id: 488129 (lineage).
- Source: https://www.fmz.com/strategy/488129 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-25 11:51:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MACD, SAR and SuperTrend. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_factor` [3.0, 2.0] x `sar_max` [0.2, 0.1]: **4 trials**; defaults 3 / 0.2 (the source's); SuperTrend ATR 10, MACD
12 / 26 / 9 and SAR step 0.02 fixed.

## Ambiguities resolved

- `ta.supertrend` direction -1 is the up-trend (Pine). Closes act on the position at the bar's start (#430850).
  REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

# #488134 多时间框架抛物线SAR动态趋势跟踪量化策略-Multi-Timeframe-Parabolic-SAR-Dynamic-Trend-Following-Quantitative-Strategy -> `fmz_488134_psar_flip_daily_psar_filter_reversal`

- FMZ source id: 488134 (lineage).
- Source: https://www.fmz.com/strategy/488134 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-25 13:22:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C265). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily SAR from completed broker days |
| 2 | PASS | Two-frame Parabolic SAR flips |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`start` [0.02, 0.01] x `maximum` [0.2, 0.1]: **4 trials**; increment = start.

## Ambiguities resolved

- The daily SAR is the last completed broker day's. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`

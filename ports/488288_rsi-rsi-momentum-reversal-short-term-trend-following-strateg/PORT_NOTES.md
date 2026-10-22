# #488288 RSI动量反转短期趋势跟踪策略与移动平均线聚合-RSI-Momentum-Reversal-Short-Term-Trend-Following-Strategy-with-Moving-Average-Confluence -> `fmz_488288_rsi2_dip_cross5_sma200_sma5_exit_long`

- FMZ source id: 488288 (lineage).
- Source: https://www.fmz.com/strategy/488288 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 16:13:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C266). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Short-RSI dip entries in an uptrend with an SMA exit |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Strategy(): capital 100000 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsiBuyLevel` [5.0, 10.0] x `exitMaLen` [5, 10]: **4 trials**; RSI 2, SMA 200.

## Ambiguities resolved

- A loop follows the position for the held-only exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`

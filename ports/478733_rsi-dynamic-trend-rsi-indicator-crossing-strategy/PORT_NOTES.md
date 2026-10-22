# #478733 动态趋势判定RSI指标交叉策略-Dynamic-Trend-RSI-Indicator-Crossing-Strategy -> `fmz_478733_rsi14_wma45_ema89_cross_reversal`

- FMZ source id: 478733 (lineage).
- Source: https://www.fmz.com/strategy/478733 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-17 16:12:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI moving-average crossings against the RSI side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG478733. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wma_length` [45, 20] x `ema_length` [89, 50]: **4 trials**; RSI 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

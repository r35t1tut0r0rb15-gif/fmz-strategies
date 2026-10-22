# #451712 基于RSIADX和一目均衡图的多因子趋势跟踪量化交易策略-Multi-factor-Trend-Following-Quantitative-Trading-Strategy-Based-on-RSI-ADX-and-Ichimoku-Cloud -> `fmz_451712_sma14_28_cross_adx_rsi_cloud_reversal`

- FMZ source id: 451712 (lineage).
- Source: https://www.fmz.com/strategy/451712 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 13:37:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with ADX, RSI and cloud filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 10] x `slow` [28, 50] x `adx_min` [20, 25]: **8 trials**; the RSI and Ichimoku lengths fixed.

## Ambiguities resolved

- Cloud edge 26 bars back. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

# #439856 基于SMA均线交叉配合市场深度指标一抛一的量化交易策略SMA-Crossover-Ichimoku-Market-Depth-Volume-Based-Quantitative-Trading-Strategy -> `fmz_439856_sma14_21_cross_ichimoku_cloud_volume_1h_reversal`

- FMZ source id: 439856 (lineage).
- Source: https://www.fmz.com/strategy/439856 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 14:21:42). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings filtered by the displaced Ichimoku cloud and volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_sma` [14, 9] x `long_sma` [21, 50]: **4 trials**; Ichimoku 9 / 26 / 52 / 26, volume SMA 20.

## Ambiguities resolved

- Cloud lines read at [26]. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

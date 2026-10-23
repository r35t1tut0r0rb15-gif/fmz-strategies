# #446538 基于向量蜡烛图的通道突破与自定义ChoCH策略-Vector-Candle-based-Channel-Breakout-and-Custom-ChoCH-Strategy -> `fmz_446538_heavy_volume_down_candle_cluster_1h_long_only`

- FMZ source id: 446538 (lineage).
- Source: https://www.fmz.com/strategy/446538 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-29 14:45:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Clusters of heavy-volume candles |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vol_mult` [2.0, 1.5] x `length` [10, 20]: **4 trials**; confirmation 3 bars, 2 needed.

## Ambiguities resolved

- Contrarian sides as written. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`

# #449710 基于修正Hull移动平均与一目均衡的量化交易策略-Quantitative-Trading-Strategy-Based-on-Modified-Hull-Moving-Average-and-Ichimoku-Kinko-Hyo -> `fmz_449710_hull12_kijun_cross_cloud_filter_reversal`

- FMZ source id: 449710 (lineage).
- Source: https://www.fmz.com/strategy/449710 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-28 13:39:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the spans from 26 bars back |
| 2 | PASS | Hull / Kijun crossings with a cloud filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`keh` [12, 20] x `displacement` [26, 13]: **4 trials**; the Ichimoku lengths fixed.

## Ambiguities resolved

- Closes after reversing entries leave them. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

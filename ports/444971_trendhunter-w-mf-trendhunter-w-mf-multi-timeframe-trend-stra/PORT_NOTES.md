# #444971 TrendHunter-w-MF-多时间框架趋势策略TrendHunter-w-MF-Multi-Timeframe-Trend-Strategy -> `fmz_444971_cloud_supertrend_ema200_confluence_reversal`

- FMZ source id: 444971 (lineage).
- Source: https://www.fmz.com/strategy/444971 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 16:01:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the cloud and EMA from completed bars |
| 2 | PASS | Cloud, SuperTrend and EMA confluence with SuperTrend exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 80 % of equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [3.0, 2.0] x `ema_len` [200, 100]: **4 trials**; the Ichimoku lengths and the ATR period fixed; the optional filters off.

## Ambiguities resolved

- Default filters only; closes act on held, non-reversed positions. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

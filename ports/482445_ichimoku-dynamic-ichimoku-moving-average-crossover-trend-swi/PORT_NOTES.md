# #482445 动态ichimoku均线突破趋势转换策略-Dynamic-Ichimoku-Moving-Average-Crossover-Trend-Switching-Strategy -> `fmz_482445_tenkan_kijun_sma2_cross_always_in`

- FMZ source id: 482445 (lineage).
- Source: https://www.fmz.com/strategy/482445 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 14:51:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Rolling extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 20] x `kijun` [26, 52]: **4 trials**; defaults 9 / 26 (the source's).

## Ambiguities resolved

- The lines are SMA 2 of the high + low sums (as written).
- The switching is a reversal. REVERSAL INTENDED (always in). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none

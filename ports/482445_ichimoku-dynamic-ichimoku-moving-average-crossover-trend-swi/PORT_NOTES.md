# #482445 动态ichimoku均线突破趋势转换策略-Dynamic-Ichimoku-Moving-Average-Crossover-Trend-Switching-Strategy -> `fmz_482445_smoothed_tenkan_kijun_cross_reversal`

- FMZ source id: 482445 (lineage).
- Source: https://www.fmz.com/strategy/482445 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 14:51:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C244). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed Tenkan / Kijun crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 20] x `kijun` [26, 60]: **4 trials**.

## Ambiguities resolved

- Unhalved 2-bar SMA lines, as written. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

# #473245 多周期均线与RSI动量交叉策略-Multi-Period-Moving-Average-and-RSI-Momentum-Cross-Strategy -> `fmz_473245_sma50_200_cross_rsi_filter_long`

- FMZ source id: 473245 (lineage).
- Source: https://www.fmz.com/strategy/473245 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:39:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_period` [50, 20] x `long_period` [200, 100]: **4 trials**; the RSI levels fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

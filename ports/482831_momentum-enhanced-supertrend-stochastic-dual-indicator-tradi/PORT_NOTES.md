# #482831 动量增强型超级趋势-随机双指标交易策略-Momentum-Enhanced-SuperTrend-Stochastic-Dual-Indicator-Trading-Strategy -> `fmz_482831_atr_band_regime_stoch_cross_always_in`

- FMZ source id: 482831 (lineage).
- Source: https://www.fmz.com/strategy/482831 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:51:10). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR bands and a stochastic. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [3.0, 2.0] x `k_len` [14, 21]: **4 trials**; defaults 3 / 14 (the source's); ATR 10 and the 3 / 3
smoothing fixed.

## Ambiguities resolved

- `ta.stoch(high, low, close, 14)` passes the high as the source, the low as "high" and the close as "low": ported as
  written (K can leave 0-100).
- The band recursion is ported as written (`max` / `min` keep the band when the close was beyond it).
- REVERSAL INTENDED; no exits (always in). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none

# #474722 高级波动率均值回归交易策略基于VIX与移动平均的多维量化交易系统-Advanced-Volatility-Mean-Reversion-Trading-Strategy-Multi-Dimensional-Quantitative-Trading-System-Based-on-VIX-and-Moving-Average -> `fmz_474722_own_price_sma10_stretch_10pct_reversal_retouch_exit`

- FMZ source id: 474722 (lineage).
- Source: https://www.fmz.com/strategy/474722 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 17:54:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C223). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA stretch entries with SMA re-touch exits |
| 3 | PASS | Exchange pair in the header only; the "VIX" request read as the same pair. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `pct` [10, 5]: **4 trials**.

## Ambiguities resolved

- The "VIX" symbol "swap" read as the header pair's own perpetual (own prices); a real VIX series is not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

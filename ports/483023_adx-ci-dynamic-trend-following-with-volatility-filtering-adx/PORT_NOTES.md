# #483023 动态趋势跟踪与波动率过滤策略基于ADX与CI双重确认的均线交叉系统-Dynamic-Trend-Following-with-Volatility-Filtering-ADX-and-CI-Dual-Confirmed-Moving-Average-Crossover-System -> `fmz_483023_sma9_21_cross_adx_chop_filter_1d`

- FMZ source id: 483023 (lineage).
- Source: https://www.fmz.com/strategy/483023 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 09:33:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages, ADX and the choppiness index. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_thresh` [20.0, 25.0] x `chop_thresh` [50.0, 61.8]: **4 trials**; defaults 20 / 50 (the source's); SMA 9 / 21,
ADX 7 and CHOP 7 fixed.

## Ambiguities resolved

- The DMI is the source's own, with `nz()` on the previous bar (the first bar's values as written).
- Closes act on the position held at the bar's start and never undo that bar's entry (as #430850); a cross without the
  filter only closes the opposite position.
- REVERSAL INTENDED. No stops. Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

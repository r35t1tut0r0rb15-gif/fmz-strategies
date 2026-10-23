# #483056 相对强弱指数与125日高点突破及成交量过滤策略-RSI-with-125-Day-High-Breakout-and-Volume-Filter-Strategy -> `fmz_483056_rsi_band_cross_125_high_fail_volume_double_reversal`

- FMZ source id: 483056 (lineage).
- Source: https://www.fmz.com/strategy/483056 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 11:15:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI band crossings and 125-day-high failures on doubled volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`high_len` [125, 250] x `vol_mult` [2.0, 1.5]: **4 trials**; RSI 14 30 / 70.

## Ambiguities resolved

- The 125-high breakout can never fire. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_reversion"`.

## Marks

`none`

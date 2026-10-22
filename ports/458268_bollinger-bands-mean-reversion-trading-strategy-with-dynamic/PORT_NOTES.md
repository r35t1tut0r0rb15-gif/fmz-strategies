# #458268 Bollinger-Bands-Mean-Reversion-Trading-Strategy-with-Dynamic-Support-布林带均值回归交易策略与动态支撑 -> `fmz_458268_close_cross_sma20_drop_stop_close_test_long`

- FMZ source id: 458268 (lineage).
- Source: https://www.fmz.com/strategy/458268 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 14:19:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C205). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop is a close test against the fill |
| 2 | PASS | Mean-line crossings with a percent stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `drop_pct` [0.02, 0.05]: **4 trials**.

## Ambiguities resolved

- Same-day guards never block on daily bars. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

# #491506 双均线回调反转交易策略基于EMA穿越与回测容差的趋势跟踪系统-Dual-EMA-Retest-Reversal-Strategy-A-Trend-Following-System-Based-on-EMA-Crossovers-and-Retest-Tolerance -> `fmz_491506_ema200_500_trend_retest_daily2_pct_bracket_reversal`

- FMZ source id: 491506 (lineage).
- Source: https://www.fmz.com/strategy/491506 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-21 15:58:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C274). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | EMA retests in an EMA-cross trend with a daily signal cap |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`retest_tolerance` [0.002, 0.001] x `stop_loss_perc` [0.005, 0.01]: **4 trials**; EMA 200 / 500, RR 4, 2 a day.

## Ambiguities resolved

- Same-side re-sends are pending. REVERSAL INTENDED. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`trailing_stop_pending`

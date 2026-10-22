# #478727 双重交叉趋势追踪策略指数均线与MACD协同交易系统-Dual-Crossover-Trend-Following-Strategy-EMA-and-MACD-Synergistic-Trading-System -> `fmz_478727_close_cross_ema9_macd_cross_swing5_stop_reversal`

- FMZ source id: 478727 (lineage).
- Source: https://www.fmz.com/strategy/478727 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 16:06:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the target base, as written |
| 2 | PASS | EMA and MACD joint crossings with a swing stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [5, 10] x `risk_mult` [3.5, 2.0]: **4 trials**; EMA 9, MACD 12 / 26 / 9.

## Ambiguities resolved

- The target exists only on a reversal (from the replaced position's price), as written; repeat re-sends not followed.
- REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

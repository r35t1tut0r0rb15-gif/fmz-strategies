# #438064 基于多时间框架移动平均线与RSI的趋势跟踪策略Trend-Following-Strategy-Based-on-Multi-Timeframe-Moving-Average-and-RSI -> `fmz_438064_ema_spread_rsi_pct_trail`

- FMZ source id: 438064 (lineage).
- Source: https://www.fmz.com/strategy/438064 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-08 16:57:29). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail |
| 2 | PASS | EMA spread and RSI levels; percent trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 13] x `trail_pct` [0.02, 0.04]: **4 trials**; slow 34, RSI 14 at 60 / 25 fixed; activation equal to the trail.

## Ambiguities resolved

- Lower-timeframe closes = the broker day's close; 2 % trail as the house percent trail. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`coarse_bar_stop, trailing_stop`

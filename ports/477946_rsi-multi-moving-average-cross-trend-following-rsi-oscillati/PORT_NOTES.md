# #477946 多均线交叉趋势跟踪RSI波动策略-Multi-Moving-Average-Cross-Trend-Following-RSI-Oscillation-Strategy -> `fmz_477946_ema20_50_pullback_sma200_trend_pct_bracket_long`

- FMZ source id: 477946 (lineage).
- Source: https://www.fmz.com/strategy/477946 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 15:15:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price exits as fractions of the fill |
| 2 | PASS | EMA pullbacks in an up-trend with a wide bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The target / stop fractions stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_threshold` [40, 50] x `near_pct` [0.01, 0.005]: **4 trials**; EMA 20 / 50, SMA 200, target 25 %, stop 10 %.

## Ambiguities resolved

- Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

# #437507 基于多时框架移动平均线和MACD-的长空开仓策略Long-and-Short-Opening-Strategy-Based-on-Multi-Timeframe-Moving-Average-and-MACD -> `fmz_437507_mtf_ema_macd_pullback_long`

- FMZ source id: 437507 (lineage).
- Source: https://www.fmz.com/strategy/437507 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-03 12:15:46). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit MACD limit -> fraction of the close; ATR structure bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, commission, slippage and the exit inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`macd_limit_frac` [0.0043, 1.0] x `stop_mult` [4.3, 3.0]: **4 trials**; every other default fixed.

## Ambiguities resolved

- 15-minute EMA = the hour's last 15-minute bar; MACD limit -> fraction; bracket from the signal bar; dead percent exits. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`

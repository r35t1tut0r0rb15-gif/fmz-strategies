# #482684 多重时间框架动态趋势跟踪策略结合EMA与ADX指标-Multi-Timeframe-Dynamic-Trend-Following-Strategy-with-EMA-and-ADX-Integration -> `fmz_482684_ema50_200_cross_adx_rsi_pct_bracket`

- FMZ source id: 482684 (lineage).
- Source: https://www.fmz.com/strategy/482684 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:52:45). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and a bracket set at entry. |
| 2 | PASS | EMAs, ADX, RSI and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 5 % of equity; commission and slippage are costs; the bracket via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [3, 6] x `sl_pct` [3, 5]: **4 trials**; defaults 3 / 3 (the source's 1.03 / 0.97); EMA 50 / 200, ADX 14 > 25
and RSI 14 (70 / 30) fixed.

## Ambiguities resolved

- The 240-minute EMAs are requested but feed no order (they would be a lower timeframe on the daily chart).
- The RSI closes act on the position held at the bar's start and never undo an entry on that bar (#430850);
  `simulate()` mirrors the house bracket from the fill (as #430254).
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first
  minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`

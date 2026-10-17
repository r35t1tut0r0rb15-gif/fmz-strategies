# #483124 多重指标交叉智能型趋势交易策略-Multi-Indicator-Cross-Intelligence-Trend-Trading-Strategy -> `fmz_483124_ema9_21_rsi_macd_pct_bracket_2d`

- FMZ source id: 483124 (lineage).
- Source: https://www.fmz.com/strategy/483124 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:54:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed bracket from the fill. |
| 2 | PASS | Moving averages, RSI, MACD and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 2.0] x `tp_pct` [2.0, 4.0]: **4 trials**; defaults 1 / 2 (the source's); EMA 9 / 21, RSI 14 and MACD
12 / 26 / 9 fixed.

## Ambiguities resolved

- The bracket uses `strategy.position_avg_price` on every bar while held: fixed from the fill.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Two-day bars are blocks of broker-day dates from 1970-01-01 (decision owed, as #426509); FREQ = "2D":
  `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

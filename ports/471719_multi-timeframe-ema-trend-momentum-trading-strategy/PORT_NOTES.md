# #471719 Multi Timeframe EMA Trend Momentum Trading Strategy -> `fmz_471719_ema_stack_pullback_daily_weekly_momentum_atr_bracket_long`

- FMZ source id: 471719 (lineage).
- Source: https://www.fmz.com/strategy/471719 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 16:35:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks; ATR bracket at entry |
| 2 | PASS | EMA-stack pullbacks with momentum filters and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pullback_pct` [1.0, 2.0] x `sl_atr` [1.5, 3.0]: **4 trials**; the 3 ATR target and lengths fixed.

## Ambiguities resolved

- Weekly series from the last completed broker week, its indicators over chart bars (as written); opening bracket kept (trailing_stop_pending). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`trailing_stop_pending`

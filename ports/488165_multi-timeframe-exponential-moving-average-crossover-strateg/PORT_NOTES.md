# #488165 多时段指数移动平均线交叉策略与趋势确认系统-Multi-Timeframe-Exponential-Moving-Average-Crossover-Strategy-with-Trend-Confirmation-System -> `fmz_488165_ema50_cross_dmi_window_bracket`

- FMZ source id: 488165 (lineage).
- Source: https://www.fmz.com/strategy/488165 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-25 16:58:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | ADAPT | 300 / 600 ticks -> 0.5 / 1 ATR; EMAs and DMI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_tz` ["UTC", "America/New_York"] x `sl_atr` [0.5, 1.0]: **4 trials**; defaults UTC / 0.5 (the source as
written: on 5-minute ETH_USDT, tick 0.01 and ATR about 6, 300 ticks are about 0.5 ATR; judgement stated before any
backtest); target 2 x the stop, EMA 50 / 200, DMI 14 and the 16:30-20:00 window fixed.

## Session open (check 9)

The entry window 16:30-20:00 (inclusive) is in the chart's time zone: UTC as written (the US afternoon), or
America/New_York (DST by the zone) as the variant. Decision owed: which reading to keep.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket.

## Ambiguities resolved

- The ADX threshold and the session string are computed but unused, as written. REVERSAL INTENDED. Stop module:
  `portfolio_kwargs` {} (D4). FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_filter"`.

## Marks

`trailing_stop_pending`

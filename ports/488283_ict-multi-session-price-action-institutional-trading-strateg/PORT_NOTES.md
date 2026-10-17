# #488283 多时段价格行为机构交易策略基于ICT理念的日内做空系统-Multi-Session-Price-Action-Institutional-Trading-Strategy-ICT-Based-Intraday-Short-System -> `fmz_488283_ict_london_sweep_tick_bracket`

- FMZ source id: 488283 (lineage).
- Source: https://www.fmz.com/strategy/488283 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-26 15:40:23). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | ADAPT | 10 / 20 ticks -> ATR multiples; session extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_tz` ["UTC", "America/New_York"] x `tick_atr` [0.0005, 0.005]: **4 trials**; defaults UTC / 0.0005 (the source
as written: a 0.01 tick on 1-hour ETH_USDT, ATR about 20, is about 0.0005 ATR; judgement stated before any backtest);
10 / 20 ticks and ATR 14 fixed.

## Session open (check 9)

London 02:00-08:20, New York 08:20-16:00 and the buy window 10:30-13:00 are clock times of the bar's open in the
chart's time zone: UTC as written, or America/New_York (DST by the zone) as the variant. Decision owed: which reading
to keep. The Asia window (19:00 to 02:00 of the same date) never matches: `asiaSell` is never emitted.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new bar (its `strategy.exit`). The port keeps
the entry's bracket (fixed at the signal bar, picked by the signal's side, re-based on the fill).

## Ambiguities resolved

- The London high / low are never reset (running extremes since the first bar, var-initialised with it), as written.
- REVERSAL INTENDED; both on one bar, the long (written last) wins. Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "session_breakout"`.

## Marks

`trailing_stop_pending`

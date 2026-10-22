# #471686 Post-Open-Breakout-Trading-Strategy-with-Dynamic-ATR-Based-Position-Management-基于ATR动态管理的开市突破交易策略 -> `fmz_471686_session_panic_candle_resistance_breakout_long`

- FMZ source id: 471686 (lineage).
- Source: https://www.fmz.com/strategy/471686 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 14:26:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Session breakouts of a touched resistance with trend filters; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and levels are constants).

## Ambiguities resolved

- Oldest swing high in the window (loop order); per-bar bracket pending (trailing_stop_pending). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`trailing_stop_pending`

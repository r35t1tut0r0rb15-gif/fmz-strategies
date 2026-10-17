# #482822 ATR动态追踪止损的趋势跟踪交易系统-ATR-Dynamic-Trailing-Stop-Trend-Following-Trading-System -> `fmz_482822_ut_bot_ema50_profit_lock`

- FMZ source id: 482822 (lineage).
- Source: https://www.fmz.com/strategy/482822 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:53:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the first profit lock a house trail, the ratchet marked. |
| 2 | PASS | An ATR trail, an EMA and percentage gains. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.1, 2.0] x `atr_len` [200, 50]: **4 trials**; defaults 1.1 / 200 (the source's); EMA 50 and the 20 % lock
fixed.

## Trailing stop (marks `trailing_stop` and `trailing_stop_pending`)

Ported natively: a close 20 % in profit moves the stop to the entry price -> `{"type": "lock_in", "gain": 0.20,
"anchor": "close"}` (the house reads minute closes; Pine the daily close).
Not expressible, not emitted: after a close 50 % in profit a second stop at entry x 1.30 (short: x 0.70), after a
close 80 % in profit a third at entry x 1.60 (short: x 0.40); each `strategy.exit` has its own id and stays once
placed, so the tightest placed level acts.

## Ambiguities resolved

- `strategy.close("Partial Profit", qty_percent = 50)` and `strategy.close("Full Exit at 100% ROI")` name no entry
  id, so they never act: no partial exit (not a criterion-1 rejection) and no ROI exit.
- Position tests read the bar-start position: a counter-signal closes and reverses. REVERSAL INTENDED.
- Stop module: `portfolio_kwargs` {} (D4). Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

`coarse_bar_stop`, `trailing_stop`, `trailing_stop_pending`

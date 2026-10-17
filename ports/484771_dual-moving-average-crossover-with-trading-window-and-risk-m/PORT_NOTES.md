# #484771 双均线交叉带定时交易窗口与止盈止损策略-Dual-Moving-Average-Crossover-with-Trading-Window-and-Risk-Management-Strategy -> `fmz_484771_sma_cross_window_tick_bracket`

- FMZ source id: 484771 (lineage).
- Source: https://www.fmz.com/strategy/484771 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-04 10:59:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket from the signal bar (moves marked). |
| 2 | ADAPT | 50 ticks -> about 1.7 ATR; moving averages. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity 2 quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_tz` ["UTC", "America/Chicago"] x `k_atr` [1.7, 3.0]: **4 trials**; defaults UTC / 1.7 (the source as written:
on 1-minute SOL_USDT, tick 0.01 and ATR about 0.3, 50 ticks are about 1.7 ATR; judgement stated before any
backtest); SMA 10 / 25 and ATR 14 fixed.

## Session open (check 9)

`market_open = hour >= 8 and minute >= 30 and hour < 15`, as written, admits only minutes 30-59 of each hour 08-14;
the close-all at 15:00. Chart time zone: UTC as written, or America/Chicago (CME hours, DST by the zone) as the
variant. Decision owed: which reading to keep.

## Trailing stop (mark `trailing_stop_pending`)

Every in-window signal moves `tradeEntryPrice`, and the exit is re-issued every bar from it: a later signal moves the
long's levels. The port keeps the entry's bracket.

## Ambiguities resolved

- The shorts get the same levels as the longs (stop below, limit above the entry): both trigger at once, so a short
  closes at the open after its fill bar (an exit signal on the fill bar; no stops for shorts).
- REVERSAL INTENDED. `simulate()` mirrors the long bracket (#430254). Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

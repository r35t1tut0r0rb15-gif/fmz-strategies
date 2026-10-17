# #491890 RSI-MA-交叉摆动交易策略与追踪止损系统-RSI-MA-Crossover-Swing-Trading-Strategy-with-Trailing-Stop-System -> `fmz_491890_rsi_sma_cross_swing_lockout`

- FMZ source id: 491890 (lineage).
- Source: https://www.fmz.com/strategy/491890 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-24 16:51:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders and close-checked exits. |
| 2 | ADAPT | The 10-point trail -> `trail_atr` x ATR(14); percentage target and stop. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital per trade and lot size quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_atr` [1.0, 2.0] x `daily_reset` [False, True]: **4 trials**; RSI 14, SMA 14 of RSI, TP 2.5 %, SL 1.5 % and the
two-loss lockout fixed (the source's).

## Session open (check 9): the loss-counter reset

As written, `if hour == 9 and minute == 15: lossCount := 0` in the chart's time zone. No 4-hour bar opens at 09:15
(in UTC or in Asia/Kolkata), so the counter never resets and the strategy stops trading after its second counted
loss (`daily_reset` False, the source as written). The inputs name Nifty options, so the evident intent is a daily
reset at the NSE open, 09:15 Asia/Kolkata (no DST): `daily_reset` True resets on the first bar each day whose open is
at or after that time. Both readings are declared in the grid before any backtest; decision owed on which to keep.

## Ambiguities resolved

- All exits are close-based signals (rule 3), in source order: trail, reversal, target / stop (the last only once
  the position is filled). Every trail exit counts as a loss, as written; the reversal exit never counts.
- The 10-point trail is re-expressed as an ATR multiple of the current bar (criterion 2; on DOGE it was unreachable).
- Entries only from flat: Opposite entries cannot occur. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

# #426794 Momentum Moving Average Breakout Strategy -> `fmz_426794_momentum_ema5`

- Source: https://www.fmz.com/strategy/426794 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-14 16:06:41). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price / tick distances -> ATR(14) multiples. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mom_atr` [0.25, 0.5, 1.0] x `tp_atr` [0.5, 1.0, 2.0]: **9 trials**, defaults 0.25 / 1.0 (the source's 50 price units and 1000 ticks, converted; the steps are a port choice).

## Ambiguities resolved

- As written shorts need momentum under +50 (not -50).
- Criterion 2 (ADAPT): momentum threshold and 1000-tick target -> ATR(14) multiples (threshold on each bar, target at the signal bar).
- Trailing stop pending (rule 2): strategy.exit(trail_points = 60 ticks) with no trail_offset. Pine arms a trailing stop only with both, so as written it may never arm; if armed it would activate after a 60-tick favourable move (6 USDT on BTC; as an ATR multiple trail_atr x ATR(14) at the signal bar). Not emitted until the project decides how to express trailing stops.
- FREQ = "30min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks (2026-10-07)

`trailing_stop_pending`

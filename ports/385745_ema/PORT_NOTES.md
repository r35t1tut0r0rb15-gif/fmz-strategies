# #385745 来自油管大神的双EMA均线策略 -> `fmz_385745_range_filter_ema_trend_flat`

- Source: https://www.fmz.com/strategy/385745 (PineScript v4/v5, author 发明者量化-小小梦, FMZ last
  modified 2022-10-10 08:57:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Loss 30 ticks -> `loss_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | Order-size lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rng_per` [20, 40] x `rng_qty` [2.5, 3.5] x `loss_atr` [1.0, 2.0] = **8 trials**. EMA 50 / 200 stay at the originals.

## Ambiguities resolved

- Loss 30 ticks -> `loss_atr` x ATR(14) at the signal bar (criterion 2); sl_stop shifted one bar.
- Tick-based trailing stop (30 / 30): rule 2, `trailing_stop_pending`, not emitted.
- Entries from flat only; simulate() mirrors the engine stop; `upon_opposite_entry="ignore"`.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks (2026-10-07)

`trailing_stop_pending`

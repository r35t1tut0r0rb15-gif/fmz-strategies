# #427314 Momentum Rotation Stock Trading Strategy -> `fmz_427314_stoch_rsi_breakout_trail`

- FMZ source id: 427314 (lineage).
- Source: https://www.fmz.com/strategy/427314 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 22:14:24). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; stop and trailing stop are house stops. |
| 2 | ADAPT | Tick distances -> ATR(14) multiples; trail activation as a fraction of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding and the per-unit bookkeeping stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [4, 2] x `trail_atr` [3, 1.5] x `activate` [0.003, 0.01]: **8 trials**; defaults 4 / 3 / 0.003; RSI 14, stochastic 14, K 3 fixed. On the source's 5-minute BTC bars with a 0.1 tick, 800 / 600 ticks are 80 / 60 USD, about 4 / 3 ATR, and 60 USD is about 0.25 % of price (judgement, stated before any backtest).

## Trailing stop (FMZ-C rule 1, mark `trailing_stop`)

As written: `strategy.exit(loss = 800, trail_points = 600, trail_offset = 600)` (ticks): a fixed stop, and from 600 ticks of profit a trailing stop 600 ticks behind the best price. Ported as `sl_stop` (ATR multiple of the signal bar) plus the house trail `{"type": "volatility", "atr_n": 14, "k": trail_atr, "anchor": "high_low", "activate_after": activate}`. Promotion of a trailing trial still needs the cTrader check (gate `trailing_ctrader_check`); a short with a trail is `not_replayable` in the exact short replay.

## Ambiguities resolved

- With pyramiding 1, the unit bookkeeping reduces to "enter from flat or reverse from the other side".
- Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop`

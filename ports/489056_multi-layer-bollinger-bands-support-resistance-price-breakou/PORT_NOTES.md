# #489056 多层布林通道支撑阻力价格突破交易策略-Multi-Layer-Bollinger-Bands-Support-Resistance-Price-Breakout-Trading-Strategy -> `fmz_489056_bb_beyond_retested_swing_stop`

- FMZ source id: 489056 (lineage).
- Source: https://www.fmz.com/strategy/489056 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-01 16:55:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at the signal bar. |
| 2 | ADAPT | Pip distances -> ATR multiples (gold scale); percentage retest band. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the stop via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sr_atr` [0.17, 0.5] x `sl_atr` [0.1, 0.5]: **4 trials**; defaults 0.17 / 0.1; BB 20 x 2 fixed. The title names
gold (pip 0.1): 25 / 15 pips are about 0.17 / 0.1 of a 4-hour gold ATR (judgement, stated before any backtest; on
the backtest's ETH_USDT they would be negligible).

## Ambiguities resolved

- The target uses strategy.position_avg_price on the flat signal bar (na): never set, as written; stop only.
- Entries only from flat: simulate() follows the house stop on bars. Opposite entries cannot occur.
- FREQ = "4h"; `coarse_bar_stop`.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop`

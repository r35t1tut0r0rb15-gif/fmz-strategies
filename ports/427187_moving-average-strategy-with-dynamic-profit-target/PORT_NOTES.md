# #427187 Moving Average Strategy with Dynamic Profit Target -> `fmz_427187_sma_turn_atr_target`

- FMZ source id: 427187 (lineage).
- Source: https://www.fmz.com/strategy/427187 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-18 21:46:47). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving target is fixed at entry (mark). |
| 2 | PASS | MA length and ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Unused ATR lot formula stored in `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [80, 40, 160] x `pt_factor` [12, 6]: **6 trials**; defaults 80 / 12 (the source's); ATR 252 fixed.

## Moving target (rule 2, mark `trailing_stop_pending`)

As written, the take-profit limit is re-placed at every bar's close at `close +- 12 x ATR(252)`, so it moves with the price (it is never active on the fill bar itself). The house trailing stop (`stops()["trail"]`) is a stop, not a moving target, so this cannot be expressed natively. The port fixes the target at entry: `tp_stop = (12 x ATR(252) / close).shift(1)` (the signal bar's value, known at the fill bar's open).

## Ambiguities resolved

- `signal` is the last entry side, not the position (after a take-profit, the same side waits for an opposite signal).
- Stop module: `portfolio_kwargs` `{}` (driver D4); one-bar reversals (REVERSAL INTENDED).
- FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`

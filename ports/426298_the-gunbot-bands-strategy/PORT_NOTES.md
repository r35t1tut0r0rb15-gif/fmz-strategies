# #426298 The Gunbot Bands Strategy -> `fmz_426298_gunbot_bbands`

- Source: https://www.fmz.com/strategy/426298 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-10 21:31:29). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price distances -> ATR(14) multiples at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0, 1, 2] x `sl_atr` [0, 1, 2] x `ts_atr` [0, 1]: **18 trials**, defaults 0 / 0 / 0 (the source's 99999e-8 price units are under one tick on BTC). Band length 15, mult 2, 25 % pulls, pyramiding gates 0 / 1 / 100, leverage 1 fixed.

## Ambiguities resolved

- `strategy()` is commented out: one position; isAdding (martingale qty) off by default, so sizing only (original_sizing.txt).
- v3 integer division: `15 / timeframe.multiplier` = 5 on 3-minute bars.
- Criterion 2 (ADAPT): ts / tp / sl / tsi price distances -> ATR(14) multiples at the latest signal bar.
- All exits are `strategy.close` on bar closes: close-based exit signals (a trail checked on closes needs no mark, rule 2).
- With nz(), the exits of a side never signalled read last_open = 0 (the short call is then always true); harmless while flat.
- FREQ = "3min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`

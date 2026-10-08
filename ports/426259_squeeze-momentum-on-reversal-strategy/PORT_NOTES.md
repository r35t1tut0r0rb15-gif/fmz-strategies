# #426259 Squeeze Momentum on Reversal Strategy -> `fmz_426259_squeeze_momentum_turn`

- Source: https://www.fmz.com/strategy/426259 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-09 23:57:41). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Strength 0.0018 price units -> `strength_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_kc` [14, 20] x `strength_atr` [0.0, 0.1, 0.25] = **6 trials**.

## Ambiguities resolved

- Strength 0.0018 (price units, forex pips) -> `strength_atr` x ATR(14) (criterion 2); 0 matches BTC.
- Squeeze flags only colour; nz(valin[1]) is that nz() (fillna(0)).
- Daily bars are broker days (17:00 New York), `FREQ = "1D"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`

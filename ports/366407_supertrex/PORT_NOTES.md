# #366407 SuperTREX -> `fmz_366407_supertrex_rsi_step`

- Source: https://www.fmz.com/strategy/366407 (PineScript v4, author Zer3192, FMZ last
  modified 2022-05-29 09:49:08). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `st_mult` [2.0, 4.0] x `st_period` [10, 20] = **8 trials**. RSI levels 35 / 70 stay at the originals.

## Ambiguities resolved

- xy is the close at the last RSI cross above 35 (0 before any); the down band ratchets on the RSI-sell close but is centred on xy, as coded.
- up_trend/down_trend history ([1]) as Pine; trend starts 1.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`

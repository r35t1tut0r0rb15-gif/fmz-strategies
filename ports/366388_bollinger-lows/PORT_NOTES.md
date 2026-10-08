# #366388 Bollinger lows -> `fmz_366388_bollinger_lows_swing`

- Source: https://www.fmz.com/strategy/366388 (PineScript v4, author Zer3192, FMZ last
  modified 2022-05-29 07:22:43). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`len5` [20, 30] x `len` [10, 20] x `period` [14, 20] = **8 trials**. Multiplier 2, lookback 100 and factor 0.001 stay at the originals.

## Ambiguities resolved

- cum() is a running sum; vp - sma(vp, 14) depends only on recent increments (start-independent).
- Swing machine with Pine nz() semantics.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`

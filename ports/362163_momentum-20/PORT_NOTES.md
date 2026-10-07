# #362163 Momentum-20 -> `fmz_362163_normalised_momentum_cross`

- Source: https://www.fmz.com/strategy/362163 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-10 10:32:54). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Momentum normalised by its own rolling stdev. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [10, 15, 30] x `base_window` [300, 450, 600] = **9 trials**. Linreg smoothing 30 fixed.

## Ambiguities resolved

- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`

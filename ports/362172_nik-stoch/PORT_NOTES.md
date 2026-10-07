# #362172 Nik-Stoch -> `fmz_362172_fast_stoch_cross_faded`

- Source: https://www.fmz.com/strategy/362172 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-10 14:08:03). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Stochastic only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_len` [5, 9, 14] x `smooth` [3, 5] = **6 trials**. %D 3 fixed.

## Ambiguities resolved

- **Direction as written**: an up-cross of %K sends a short. Flagged in the worker report.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks (2026-10-07)

`none`

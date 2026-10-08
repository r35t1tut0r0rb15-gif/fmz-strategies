# #426136 Simple EMA20 Strat -> `fmz_426136_ema20_stoch_long_only`

- Source: https://www.fmz.com/strategy/426136 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-08 15:56:24). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A19). Not run.

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

`ema_len` [10, 20, 50] x `period_k` [9, 14] = **6 trials**.

## Ambiguities resolved

- Long only, as written (rule 6).
- Entry (low > EMA) and exit (close < EMA) cannot coincide.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

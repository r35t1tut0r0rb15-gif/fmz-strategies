# #365080 ogcheckers_1hr_scalp_ema_sma_rsi -> `fmz_365080_red_bar_rsi_extreme`

- Source: https://www.fmz.com/strategy/365080 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-23 14:25:26). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

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

`rsi_upper` [70, 75] x `rsi_buffer` [5, 10] = **4 trials**.

## Ambiguities resolved

- EMA/SMA flags and the daily request.security values never reach the orders: not ported.
- Orders use RSI(7) of open whatever `rsi_length` says; higher RSI -> long kept as written.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`

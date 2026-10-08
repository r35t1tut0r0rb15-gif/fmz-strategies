# #425882 EMA200 and Stochastic RSI Strategy -> `fmz_425882_ema200_stochrsi_strong_bar`

- Source: https://www.fmz.com/strategy/425882 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-06 11:28:53). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`wick_pct` [20, 40] x `change_pct` [0.25, 0.5] x `ema_len` [100, 200] = **8 trials**.

## Ambiguities resolved

- Short wick test |high - open| / |high - close| kept as written (not the long test mirrored).
- ATR stop lines and reward/risk input only draw.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks (2026-10-07)

`none`

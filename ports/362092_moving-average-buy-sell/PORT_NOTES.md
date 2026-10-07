# #362092 Moving-Average-Buy-Sell -> `fmz_362092_ema_20_200_cross`

- Source: https://www.fmz.com/strategy/362092 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 23:46:33). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMA cross only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wave` [10, 20, 50] x `tide` [100, 200] = **6 trials**.

## Ambiguities resolved

- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

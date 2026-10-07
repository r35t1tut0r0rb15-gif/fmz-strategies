# #362000 Heikin-Ashi-Trend -> `fmz_362000_heikin_ashi_ema_trend`

- Source: https://www.fmz.com/strategy/362000 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 14:33:57). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; HA series of the same timeframe. |
| 2 | PASS | Average comparisons only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [50, 77, 100] x `smooth` [10, 21, 30] = **9 trials**.

## Ambiguities resolved

- The HA ticker is reproduced from the bars (standard HA recursion).
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks (2026-10-07)

`none`

# #362443 Swing-High-Low-Indicator-w-MACD-and-EMA-Confirmations -> `fmz_362443_ema_20_50_side`

- Source: https://www.fmz.com/strategy/362443 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-11 16:33:11). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A8). Not run.

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

`fast` [10, 20, 30] x `slow` [50, 100] = **6 trials**.

## Ambiguities resolved

- Only the EMA trend sends orders; swing detection and MACD confirmations are labels.
- `FREQ = "4h"` from the backtest header (equal to the requested 240-minute resolution).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

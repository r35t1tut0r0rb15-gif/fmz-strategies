# #362004 RSI-Buy-Sell-Signals -> `fmz_362004_envelope_cross_faded`

- Source: https://www.fmz.com/strategy/362004 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 15:14:58). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | +/-0.22 % envelope -> +/- `env_atr` x ATR(14). |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [8, 14, 20] x `env_atr` [0.1, 0.25, 0.5] = **9 trials**.

## Ambiguities resolved

- **Direction as written**: `cross_sell` sends a long and `cross_buy` a short. Flagged in the worker report.
- The RSI part of the title only drives labels/alerts.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_reversion"`.

## Marks (2026-10-07)

`none`

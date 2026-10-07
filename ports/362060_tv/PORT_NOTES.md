# #362060 tv高低点策略 -> `fmz_362060_macd_cross_divergence`

- Source: https://www.fmz.com/strategy/362060 (PineScript v4, author Zer3192, FMZ last
  modified 2022-05-27 05:34:08). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; compares with the previous cross bar only. |
| 2 | PASS | Divergence tests are relative. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [21, 26, 34] = **6 trials**. Signal 9 fixed.

## Ambiguities resolved

- `barssince(cross[1])` points at the previous cross bar strictly before the current bar; reproduced by tracking the last cross index.
- `FREQ = "4h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks (2026-10-07)

`none`

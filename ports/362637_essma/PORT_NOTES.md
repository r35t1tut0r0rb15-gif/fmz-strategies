# #362637 ESSMA -> `fmz_362637_essma_cross`

- Source: https://www.fmz.com/strategy/362637 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-12 15:20:54). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`length` [20, 50, 100] = **3 trials**.

## Ambiguities resolved

- The five weights cancel (each average is linear in its input), so they are not parameters.
- The SMMA recursion on `smma[2]` is kept as written.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

# #361554 ADX-and-DI-for-v4 -> `fmz_361554_di_side_reverse`

- Source: https://www.fmz.com/strategy/361554 (PineScript v4, FMZ last modified 2022-05-07 16:31:36).
  Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pine bar-close evaluation, next-open fills. |
| 2 | PASS | DI ratio only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`length` [7, 14, 21] = **3 trials**. `th` (20) is an unused plot level.

## Ambiguities resolved

- ADX and the `th` threshold are computed/declared but not used by the orders.
- Warm-up: no orders for the first `len` bars (the source trades from bar 0 on the zero-seeded sums).
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks (2026-10-07)

`none`

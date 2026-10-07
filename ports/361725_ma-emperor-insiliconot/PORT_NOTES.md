# #361725 MA-Emperor-insiliconot -> `fmz_361725_lowpass_filter_cross`

- Source: https://www.fmz.com/strategy/361725 (PineScript v3, author ChaoZhang (insiliconot indicator), FMZ last
  modified 2022-05-08 00:11:51). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Filter cross only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_fast` [8, 13, 21] x `len_slow` [21, 34, 55] = **9 trials** (pairs with fast >= slow are degenerate; kept for a full grid).

## Ambiguities resolved

- Only the default filter (LowPass) of 14 options is ported.
- Warm-up: no orders for the first 100 bars (the zero-seeded recursion).
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

# #426502 Momentum Moving Average Persistent Long Trading Strategy -> `fmz_426502_ohlc4_momentum_long`

- Source: https://www.fmz.com/strategy/426502 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-12 16:15:44). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A22). Not run.

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

`up_bars` [3, 5] x `down_bars` [3, 4]: **4 trials**, defaults 5 / 4 (the source's).

## Ambiguities resolved

- Long only; the risk input is unused.
- 3-day bars from broker days in fixed blocks counted from 1970-01-01 (phase is a port choice; decision owed).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks (2026-10-07)

`none`

# #426801 ATR Dynamic Profit Target and Stop Loss Strategy -> `fmz_426801_volatility_stop`

- Source: https://www.fmz.com/strategy/426801 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-14 16:22:53). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

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

`length` [10, 20, 30] x `mult` [1, 2, 3]: **9 trials**, defaults 20 / 1 (the source's).

## Ambiguities resolved

- As written nz() starts the running min and the stop at 0; na (ATR warm-up) propagates through max / min as in Pine, so the first valid stop flips the warm-up state.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`

# #362457 3-Supertrend-Add-In-This-Single-Script -> `fmz_362457_three_supertrend_agree`

- Source: https://www.fmz.com/strategy/362457 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-11 17:04:21). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`f1` [1, 1.5] x `f2` [2, 2.5] x `f3` [3, 4] = **8 trials**. ATR lengths 21/14/7 fixed.

## Ambiguities resolved

- Same idea as #361880 (triple SuperTrend) with different settings and no early exit; not an exact duplicate.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`

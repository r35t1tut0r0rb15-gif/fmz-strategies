# #426571 Kase Dynamic Stop Loss Strategy -> `fmz_426571_kase_dev_stop`

- Source: https://www.fmz.com/strategy/426571 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-13 14:08:47). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A23). Not run.

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

`length` [20, 30, 50] x `level` [2, 3, 4]: **9 trials**, defaults 30 / 4 (the source's).

## Ambiguities resolved

- Warm-up: `close < na` is false, so the source is long until Val4 exists.
- Level k uses k - 1 SDs (Val1..Val4 of the source).
- Pine population stdev; "Trade reverse" off.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks (2026-10-07)

`none`

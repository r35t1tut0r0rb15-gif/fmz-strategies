# #364037 EMA TREND CLOUD -> `fmz_364037_ema_cross_cloud`

- Source: https://www.fmz.com/strategy/364037 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-18 16:08:03). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

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

`fast` [9, 10] x `slow` [18, 20] = **4 trials** (input defaults and the header args).

## Ambiguities resolved

- Defaults 9/20 from input(); the header args 10/18 are in the grid.
- Alerts only; no other logic.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

# #362572 3EMA -> `fmz_362572_three_ema_pullback_zone`

- Source: https://www.fmz.com/strategy/362572 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-12 01:35:20). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`short` [10, 20] x `mid` [50, 60] x `long` [100, 200] = **8 trials**.

## Ambiguities resolved

- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks (2026-10-07)

`none`

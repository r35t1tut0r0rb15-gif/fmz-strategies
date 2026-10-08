# #426483 Quadruple EMA Indicators Trading Strategy -> `fmz_426483_dema_change_ema_cross_units`

- Source: https://www.fmz.com/strategy/426483 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-12 14:53:22). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`ema_slow` [44, 21] x `ema_fast` [72, 100] x `length` [14, 21]: **8 trials**, defaults 44 / 72 / 14 (the source's).

## Ambiguities resolved

- `security(res = "120")` on 2h bars is the chart series.
- `strategy.order` adds +-1 unit; alternating crosses give +1 / 0 or -1 / 0 depending on the first cross in the data (data-start dependence; decision owed).
- FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

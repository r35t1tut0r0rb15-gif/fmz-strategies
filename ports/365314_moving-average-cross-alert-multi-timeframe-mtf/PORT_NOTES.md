# #365314 Moving Average Cross Alert, Multi-Timeframe Option (MTF) (by ChartArt) -> `fmz_365314_ema_cross_close_confirm`

- Source: https://www.fmz.com/strategy/365314 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2022-05-24 11:23:02). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

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

`short` [20, 50] x `long` [100, 200] = **4 trials**.

## Ambiguities resolved

- "Use Current Timeframe" default true: no higher-timeframe read.
- MA type default 2 (EMA); the cross needs strict inequality on the previous bar (`TrendingDown()[1]`).
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`

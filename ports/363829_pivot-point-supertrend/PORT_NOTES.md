# #363829 Pivot Point SuperTrend -> `fmz_363829_pivot_point_supertrend`

- Source: https://www.fmz.com/strategy/363829 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-17 16:03:36). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

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

`prd` [2, 3, 5] x `factor` [2.0, 3.0] x `atr_period` [6, 10] = **12 trials**.

## Ambiguities resolved

- Pivots confirmed `prd` bars later (no look-ahead); a pivot value of 0 counts as none (Pine float-as-bool).
- Same pivot-centre trend as the ATR module of #363766.
- `FREQ = "1min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`

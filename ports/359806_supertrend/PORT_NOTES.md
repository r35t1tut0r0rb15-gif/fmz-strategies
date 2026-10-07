# #359806 超级趋势策略SuperTrend -> `fmz_359806_supertrend_slope_filter`

- Source: https://www.fmz.com/strategy/359806 (PineScript, FMZ last modified 2024-08-30 18:24:36).
  Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pine bar-close evaluation, next-open fills. |
| 2 | PASS | ATR-factor bands. |
| 3 | PASS | Binance spot pair in the header only. |
| 4 | DONE | `default_qty_value = 50` % of equity -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same indicator family as #200625 (different rules). |
| 7 | IGNORED | The description's performance remarks are not used. |

## Declared grid (criterion 5)

`factor` [3, 5, 7] x `atr_period` [7, 10, 14] = **9 trials**.

## Ambiguities resolved

- The slope filter compares with 2 bars back on the long side and 3 bars back on the short side,
  as written (asymmetric).
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`

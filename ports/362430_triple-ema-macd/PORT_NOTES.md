# #362430 Triple-EMA-MACD -> `fmz_362430_macd_cross_ema_trend`

- Source: https://www.fmz.com/strategy/362430 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-11 16:17:19). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A8). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | `default_qty_value = 750` in strategy() -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 26] x `slow` [49, 60] x `trend_slow` [150, 200] = **8 trials**.

## Ambiguities resolved

- `SMema < LGema` for shorts is read as 'not above' (equal EMAs are a measure-zero case).
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`

# #362178 Diamond-Trend -> `fmz_362178_psar_regression_band_flip`

- Source: https://www.fmz.com/strategy/362178 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-10 14:47:48). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | SAR and residual bands come from the bars. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND362178` (Jaccard 0.65-0.80) with #367476 (PORT_CANDIDATE); best Jaccard 0.704 with #367476. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [50, 100, 200] x `dev` [1.5, 1.9, 2.5] = **9 trials**. SAR 0.02/0.02/0.2 fixed.

## Ambiguities resolved

- `ta.sar` is TradingView's documented algorithm (not TA-Lib's, which #224799 uses).
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks (2026-10-07)

`none`

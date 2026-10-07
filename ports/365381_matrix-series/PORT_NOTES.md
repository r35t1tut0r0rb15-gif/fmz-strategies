# #365381 Matrix Series -> `fmz_365381_matrix_series_extreme`

- Source: https://www.fmz.com/strategy/365381 (PineScript (mixed v4/v5), author ChaoZhang, FMZ last
  modified 2022-05-24 16:42:26). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`smoother` [3, 5, 8] x `level` [100, 200] (symmetric) = **6 trials**.

## Ambiguities resolved

- The plotted shapes act as booleans (defined and non-zero); undefined when up == down.
- Overbought -> long, oversold -> short: kept as written. CCI support/resistance lines only draw.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`

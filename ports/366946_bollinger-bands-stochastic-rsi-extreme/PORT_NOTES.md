# #366946 Bollinger Bands Stochastic RSI Extreme Signal -> `fmz_366946_bb_stochrsi_extreme_inverse`

- Source: https://www.fmz.com/strategy/366946 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-31 19:16:17). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A15). Not run.

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

`length` [20, 40] x `mult` [1.5, 2.0] x `limit` [80, 90] (symmetric) = **8 trials**.

## Ambiguities resolved

- Bear signal enters long, Bull enters short: inverted relative to the names, kept as written.
- Population stdev; stoch RSI 14/14/3/3.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`

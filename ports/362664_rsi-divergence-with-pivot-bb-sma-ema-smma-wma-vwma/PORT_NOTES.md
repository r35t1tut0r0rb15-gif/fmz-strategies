# #362664 RSI Divergences with Pivots, BB, MA -> `fmz_362664_rsi_divergence_inverse`

- Source: https://www.fmz.com/strategy/362664 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-12 17:45:45). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`rsi_period` [7, 14, 21] x `lookback` [45, 90] = **6 trials**.

## Ambiguities resolved

- The bearish divergence enters long and the bullish one short: inverted relative to the names, kept as written.
- `highestbars == 0` read as the current RSI equalling the 90-bar RSI high (ties go to the current bar).
- RSI-MA/Bollinger plots and pivot flags do not reach the orders; not ported.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`

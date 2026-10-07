# #365359 Relative Strength Index - Divergences - Libertus -> `fmz_365359_rsi_divergence_libertus`

- Source: https://www.fmz.com/strategy/365359 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-24 15:25:05). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
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

`rsi_period` [7, 14, 21] x `lookback` [45, 90] = **6 trials**.

## Ambiguities resolved

- `highestbars == 0` read as the current RSI equalling the 90-bar RSI high (ties to the current bar).
- Same engine as #362664 with the orders the right way round.
- No bar size in the source: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`bar_size_pending`

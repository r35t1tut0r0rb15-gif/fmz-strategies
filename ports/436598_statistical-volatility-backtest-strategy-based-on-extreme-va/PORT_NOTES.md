# #436598 Statistical Volatility Backtest Strategy Based on Extreme Value Method -> `fmz_436598_extreme_value_volatility_state`

- FMZ source id: 436598 (lineage).
- Source: https://www.fmz.com/strategy/436598 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-26 10:24:53). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C92). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility estimate state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [30, 60] x `top_band` [0.005, 0.01]: **4 trials**; the low band 0.0016 and the reverse switch (off) fixed.

## Ambiguities resolved

- State entries sent on every bar of the state. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_regime"`.

## Marks

`none`

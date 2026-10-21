# #437007 Dynamic Trailing Stop Optimization Strategy Based on Ichimoku Cloud -> `fmz_437007_inverse_fisher_stoch_cross`

- FMZ source id: 437007 (lineage).
- Source: https://www.fmz.com/strategy/437007 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 14:40:47). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C98). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Stochastic levels; the tick trail is pending |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, commission and the trailing inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_len` [19, 14] x `wma_len` [4, 6]: **4 trials**; levels 82.05 / 19 fixed; the trailing stop is pending.

## Ambiguities resolved

- Trailing stop: activation dtsiv ticks (RSI of ATR / 68.3 x 245 at the second-latest signal), offset dtsov ticks (2-bar SMA of a 1-minute ATR x 100 at the second-latest signal); not expressible, pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`trailing_stop_pending`

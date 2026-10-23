# #458244 Multi Timeframe Unified Strategy Based on Quantitative Momentum and Convergence Divergence -> `fmz_458244_scalp_swing_ma_cross_squeeze_momentum_long_only`

- FMZ source id: 458244 (lineage).
- Source: https://www.fmz.com/strategy/458244 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:33:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MA crossings filtered by the squeeze state and momentum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 2.5] x `kc_mult` [1.5, 2.0]: **4 trials**; EMA 5 / 15, SMA 20 / 50, lengths 20.

## Ambiguities resolved

- One long at a time, closed only by its own id. Volume not used. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "squeeze_momentum"`.

## Marks

`none`

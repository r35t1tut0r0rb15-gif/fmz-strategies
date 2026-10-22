# #443124 The Momentum Breakout Strategy -> `fmz_443124_buy_low_sell_high_10bar_bands_long`

- FMZ source id: 443124 (lineage).
- Source: https://www.fmz.com/strategy/443124 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 14:04:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C166). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Distance from the 10-bar extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_threshold` [0.02, 0.05] x `sell_threshold` [0.02, 0.05]: **4 trials**; the 10-bar window fixed.

## Ambiguities resolved

- Entry first, the close on held longs only. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

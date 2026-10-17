# #435010 Momentum Tracking Adaptive Statistical Arbitrage Strategy -> `fmz_435010_nadaraya_watson_kernel_long`

- FMZ source id: 435010 (lineage).
- Source: https://www.fmz.com/strategy/435010 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-11 16:41:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Kernel-smoothed price levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 20 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`h` [8, 16] x `x0` [25, 8]: **4 trials**; relative weighting 8 fixed.

## Ambiguities resolved

- Kernel window and x_0 as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`

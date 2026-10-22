# #452712 Dynamic Market Regime Identification Strategy Based on Linear Regression Slope -> `fmz_452712_close_slope_regime_sma50_cross_exit_reversal`

- FMZ source id: 452712 (lineage).
- Source: https://www.fmz.com/strategy/452712 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 13:51:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C189). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the price-unit threshold as a fraction of 42000 |
| 2 | PASS | Slope regimes with SMA-cross exits |
| 3 | PASS | Spot pair in the header only (the source sends shorts as written). |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slope_len` [20, 10] x `sma_len` [50, 100] x `thr_frac` [2.38e-06, 0.001]: **8 trials**.

## Ambiguities resolved

- Threshold 0.1 as a fraction of 42000. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

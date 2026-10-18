# #435264 Adaptive Price Zone Reversal Trading Strategy -> `fmz_435264_adaptive_price_zone_fade`

- FMZ source id: 435264 (lineage).
- Source: https://www.fmz.com/strategy/435264 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 16:33:33). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [False, True] x `n_periods` [20, 40] x `band_pct` [2, 1]: **8 trials**.

## Ambiguities resolved

- State changes only; long side first on a bar touching both bands. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_band"`.

## Marks

`none`

# #458248 Multi Indicator Trend Following with Volume Confirmation Strategy -> `fmz_458248_tasc_vcts_adx_tti_vpci_long_only`

- FMZ source id: 458248 (lineage).
- Source: https://www.fmz.com/strategy/458248 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:43:53). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX trend filter with volume-weighted thrust and price-volume confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [30.0, 25.0] x `long_vp` [25, 50]: **4 trials**; ADX 14 / 14, TTI 13 / 26 / 9, VPCI short 5.

## Ambiguities resolved

- Volume = broker tick volume (VWMAs and VPCI). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_trend"`.

## Marks

`none`

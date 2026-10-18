# #435867 Dynamic Re entry Buy only Strategy -> `fmz_435867_sma_cross_weekly_cci_reentry_long`

- FMZ source id: 435867 (lineage).
- Source: https://www.fmz.com/strategy/435867 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-19 13:56:55). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C82). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the weekly value from completed weeks |
| 2 | PASS | Average cross, CCI and a directional index |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `adx_threshold` [25, 20]: **4 trials**; SMA 30 / 100, CCI 14 and ADX 14 fixed.

## Ambiguities resolved

- Last completed week; script's own ADX; orders in call order. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "cci_oscillator"`.

## Marks

`none`

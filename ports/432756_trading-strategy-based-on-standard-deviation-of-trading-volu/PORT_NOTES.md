# #432756 Trading Strategy Based on Standard Deviation of Trading Volume -> `fmz_432756_sma20_slope_volume_stdev_gate_reversal`

- FMZ source id: 432756 (lineage).
- Source: https://www.fmz.com/strategy/432756 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-21 11:11:51). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average slope with a low-volume gate |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [40, 20] x `factor` [1.0, 0.5]: **4 trials**; nlow 5, options 1.

## Ambiguities resolved

- Adjusted volume as the code does it (not as the comment says). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_filter"`.

## Marks

`none`

# #432240 Volume Flow Indicator Based Trend Following Strategy -> `fmz_432240_volume_flow_indicator_signal_cross_long`

- FMZ source id: 432240 (lineage).
- Source: https://www.fmz.com/strategy/432240 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-15 17:53:51). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume flow indicator against its signal |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vfi_len` [130, 50] x `coef` [0.2, 0.1]: **4 trials**; vcoef 2.5, signal 5.

## Ambiguities resolved

- Author's year gate dropped. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`none`

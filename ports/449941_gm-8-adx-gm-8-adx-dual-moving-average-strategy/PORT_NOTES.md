# #449941 GM-8-ADX-双均线策略-GM-8-ADX-Dual-Moving-Average-Strategy -> `fmz_449941_sma15_cross_ema59_side_signed_dx_reversal`

- FMZ source id: 449941 (lineage).
- Source: https://www.fmz.com/strategy/449941 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 15:50:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with an EMA side and a directional filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 0.4 lot stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [34.0, 20.0] x `adx_period` [8, 14]: **4 trials**; the SMA 15 and EMA 59 fixed.

## Ambiguities resolved

- Script's signed directional index. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`

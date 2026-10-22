# #478690 趋势追踪优化双T3指标策略-Optimized-Dual-T3-Trend-Tracking-Strategy -> `fmz_478690_t3_vs_ott_band_williams_r_long`

- FMZ source id: 478690 (lineage).
- Source: https://www.fmz.com/strategy/478690 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 14:29:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | T3 against an OTT band with a Williams %R filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`t3_length` [5, 10] x `tott_coeff` [0.006, 0.01]: **4 trials**; T3 opt 0.1, TOTT 5 / 0.1, %R 3.

## Ambiguities resolved

- One parameter set for buy and sell (equal by default). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_tracker"`.

## Marks

`none`

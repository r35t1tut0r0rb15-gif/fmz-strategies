# #438019 动量双滑窗TSI指标Momentum-Dual-Moving-Window-TSI-Indicator -> `fmz_438019_tsi_signal_cross_daily`

- FMZ source id: 438019 (lineage).
- Source: https://www.fmz.com/strategy/438019 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-08 11:20:35). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | TSI signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital, percent-of-equity size, commission and pyramiding stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long` [25, 40] x `short` [13, 7]: **4 trials**; signal 13 fixed.

## Ambiguities resolved

- Lower-timeframe close = the broker day's close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

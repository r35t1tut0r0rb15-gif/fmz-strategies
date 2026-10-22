# #482769 Dual Moving Average Trend Following System with Adaptive Dynamic Filtering Strategy -> `fmz_482769_sma100_200_up_bar_wpr_rising_quiet_prev_long`

- FMZ source id: 482769 (lineage).
- Source: https://www.fmz.com/strategy/482769 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend-side up bars with a %R momentum filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ma` [100, 50] x `run_up_threshold` [0.5, 1.0]: **4 trials**; SMA(SMA, 200), %R 14, -20 / -80.

## Ambiguities resolved

- The previous-day branch cannot fire on positive prices, as written. Long only. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

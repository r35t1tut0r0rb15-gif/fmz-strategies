# #482591 Adaptive Dual Indicator Cross Smart Timing Trading Strategy -> `fmz_482591_rsi14_cci20_extreme_stay_entry_relative_exit_reversal`

- FMZ source id: 482591 (lineage).
- Source: https://www.fmz.com/strategy/482591 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-19 10:56:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C247). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI / CCI extreme stays with exits relative to the entry readings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_length` [20, 14] x `rsi_exit_length` [30, 14]: **4 trials**; zones 31 / -120, 69 / 120, stay 2, exits +12 / -8 / 100.

## Ambiguities resolved

- The short's stay test is <= 2 bars, as written. The timeframe switch takes its default branch (chart "60").
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

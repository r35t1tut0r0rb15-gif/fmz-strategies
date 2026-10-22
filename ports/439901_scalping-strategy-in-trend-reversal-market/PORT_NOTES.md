# #439901 Scalping Strategy in Trend Reversal Market -> `fmz_439901_trapped_countertrend_scalp_state`

- FMZ source id: 439901 (lineage).
- Source: https://www.fmz.com/strategy/439901 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 17:43:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C127). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_b` [60, 30] x `rsi_ct` [35.0, 25.0]: **4 trials**; RSI 5, smoothing 13, window 15 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`

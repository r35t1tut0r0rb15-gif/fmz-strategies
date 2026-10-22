# #446553 Modified Relative Strength Index Trend Following Strategy -> `fmz_446553_rsi_of_ema13_signal_cross_reversal`

- FMZ source id: 446553 (lineage).
- Source: https://www.fmz.com/strategy/446553 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-29 16:16:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C176). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed-RSI signal crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [13, 5] x `rsi_len` [14, 7]: **4 trials**; the signal EMA 5 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

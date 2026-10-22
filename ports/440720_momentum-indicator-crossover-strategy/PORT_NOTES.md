# #440720 Momentum Indicator Crossover Strategy -> `fmz_440720_rsi3_gap_sma_zero_cross_long`

- FMZ source id: 440720 (lineage).
- Source: https://www.fmz.com/strategy/440720 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-01 14:50:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C139). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed RSI gap |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [3, 7] x `length3` [13, 21]: **4 trials**; SMA 21 and threshold 0 fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

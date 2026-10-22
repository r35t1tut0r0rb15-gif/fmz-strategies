# #454737 Multi Period Exponential Moving Average Crossover Strategy with Options Trading Suggestion System -> `fmz_454737_ema9_50_cross_reversal`

- FMZ source id: 454737 (lineage).
- Source: https://www.fmz.com/strategy/454737 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 14:41:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `longer_len` [50, 100]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

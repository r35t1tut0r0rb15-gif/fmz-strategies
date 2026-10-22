# #454362 Trend Following Adaptive Expected Value Assessment Strategy Based on Crossover Moving Averages -> `fmz_454362_sma14_28_cross_reversal`

- FMZ source id: 454362 (lineage).
- Source: https://www.fmz.com/strategy/454362 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 16:29:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 7] x `slow` [28, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

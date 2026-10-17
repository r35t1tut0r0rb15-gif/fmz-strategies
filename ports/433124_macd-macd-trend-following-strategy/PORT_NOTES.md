# #433124 MACD趋势追踪策略MACD-Trend-Following-Strategy -> `fmz_433124_macd_hist_zero_cross`

- FMZ source id: 433124 (lineage).
- Source: https://www.fmz.com/strategy/433124 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-24 15:51:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | A MACD histogram sign |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 17]: **4 trials**; signal 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`

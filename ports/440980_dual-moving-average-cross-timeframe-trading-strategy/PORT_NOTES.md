# #440980 Dual Moving Average Cross Timeframe Trading Strategy -> `fmz_440980_ema6_jma14_cross_long`

- FMZ source id: 440980 (lineage).
- Source: https://www.fmz.com/strategy/440980 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 15:03:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA / JMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lenma_fast` [6, 12] x `lenma_slow` [14, 28]: **4 trials**.

## Ambiguities resolved

- Long only (default trade type). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

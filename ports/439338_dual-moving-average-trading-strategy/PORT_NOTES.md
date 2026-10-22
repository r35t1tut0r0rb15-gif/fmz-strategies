# #439338 Dual Moving Average Trading Strategy -> `fmz_439338_ema5_15_cross_bar_size_pending`

- FMZ source id: 439338 (lineage).
- Source: https://www.fmz.com/strategy/439338 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-19 14:10:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | No exchange named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_length` [5, 10] x `ma2_length` [15, 30]: **4 trials**; the bar size is the driver's.

## Ambiguities resolved

- No chart period in the source: bar size pending. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`bar_size_pending`

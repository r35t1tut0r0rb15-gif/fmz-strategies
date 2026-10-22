# #439738 Triple Moving Average Quantitative Trading Strategy -> `fmz_439738_sma13_50_cross_sma200_side`

- FMZ source id: 439738 (lineage).
- Source: https://www.fmz.com/strategy/439738 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 14:20:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings and an SMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [13, 20] x `ma2` [50, 100]: **4 trials**; SMA 200 fixed.

## Ambiguities resolved

- Date window dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

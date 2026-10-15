# #427303 Dual Moving Average Crossover Strategy with Multi-Type Moving Averages -> `fmz_427303_multi_x_ma_cross_long`

- FMZ source id: 427303 (lineage).
- Source: https://www.fmz.com/strategy/427303 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-19 21:27:31). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1_len` [9, 20] x `ma2_len` [21, 50] x `ma3_on` [False, True]: **8 trials**; defaults 9 / 21 / False (the source's: EMA 9, SMA 21, MA 3 off).

## Ambiguities resolved

- VWMA (volume) is not offered as an MA type (check 8).
- With MA 3 on, the cross needs close above the MA 3 of highs, and a close crossing above it also enters (as written).
- Long only. FREQ = "1min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

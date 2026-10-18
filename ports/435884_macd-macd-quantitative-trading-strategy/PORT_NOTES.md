# #435884 运用MACD量化交易策略MACD-Quantitative-Trading-Strategy -> `fmz_435884_oversold_macd_cross_long`

- FMZ source id: 435884 (lineage).
- Source: https://www.fmz.com/strategy/435884 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-19 15:11:57). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit level -> fraction of the close |
| 3 | PASS |  |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `level_frac` [0.00023, 0.001]: **4 trials**; slow 26 and signal 9 fixed.

## Ambiguities resolved

- Price-unit level -> fraction of the close. Long only. FREQ = "bar_size_pending" (no bar size in the source).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`bar_size_pending`

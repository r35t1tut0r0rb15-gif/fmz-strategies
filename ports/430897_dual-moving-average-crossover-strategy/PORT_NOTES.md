# #430897 Dual Moving Average Crossover Strategy -> `fmz_430897_sma_10_13_cross_stop`

- FMZ source id: 430897 (lineage).
- Source: https://www.fmz.com/strategy/430897 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 17:04:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed percentage stop |
| 2 | PASS | SMA crosses and a percentage stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [13, 30] x `stop_pct` [1.0, 3.0]: **4 trials**; SMA 10 fixed.

## Ambiguities resolved

- Stop from the fill bar (the source starts it one bar later). Mark coarse_bar_stop. REVERSAL INTENDED.
  FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

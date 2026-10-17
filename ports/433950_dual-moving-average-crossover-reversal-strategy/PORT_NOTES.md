# #433950 Dual Moving Average Crossover Reversal Strategy -> `fmz_433950_sma_cross_5bar_exit`

- FMZ source id: 433950 (lineage).
- Source: https://www.fmz.com/strategy/433950 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 16:56:43). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-count exit signals |
| 2 | PASS | Moving-average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold` [5, 10] x `trend_len` [50, 100]: **4 trials**; SMA 9 / 14 fixed.

## Ambiguities resolved

- Bar-count exits from each signal. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

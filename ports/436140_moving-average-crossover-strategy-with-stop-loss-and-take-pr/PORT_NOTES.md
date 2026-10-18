# #436140 Moving Average Crossover Strategy with Stop Loss and Take Profit -> `fmz_436140_sma_9_55_cross_atr_bracket_long`

- FMZ source id: 436140 (lineage).
- Source: https://www.fmz.com/strategy/436140 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 15:52:57). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick-typed levels read as the intended ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [1.0, 2.0] x `rr` [2.0, 3.0]: **4 trials**; SMA 9 / 55 and ATR 14 fixed.

## Ambiguities resolved

- Tick-typed levels read as the intended 1 : 2 ATR bracket. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

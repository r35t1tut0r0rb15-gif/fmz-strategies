# #432768 双SMA均线交叉交易策略Dual-Moving-Average-Crossover-Trading-Strategy -> `fmz_432768_sma_cross_long_bracket`

- FMZ source id: 432768 (lineage).
- Source: https://www.fmz.com/strategy/432768 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-21 12:26:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick-scaled distances -> percentages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital-based position size, compounding and commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [10.1, 1.0] x `sl_pct` [9.9, 1.0]: **4 trials**; SMA 14 / 28 fixed.

## Ambiguities resolved

- Prices passed as ticks: bracket as written (about 10 %), the 1 % intent in the grid. Shorts unbracketed as written. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

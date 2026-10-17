# #434593 EMA动量均线交叉策略EMA-Momentum-Moving-Average-Crossover-Strategy -> `fmz_434593_ema_7_21_cross_atr_stop`

- FMZ source id: 434593 (lineage).
- Source: https://www.fmz.com/strategy/434593 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-07 17:00:52). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C69). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | ADAPT | Tick stop -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 14] x `sl_atr` [0.2, 1.5]: **4 trials**; EMA 21 and ATR 14 fixed.

## Ambiguities resolved

- Tick stop -> 0.2 ATR. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

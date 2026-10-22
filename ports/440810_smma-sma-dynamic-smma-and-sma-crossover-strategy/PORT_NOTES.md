# #440810 动态SMMA与SMA交叉策略Dynamic-SMMA-and-SMA-Crossover-Strategy -> `fmz_440810_sma20_50_cross_tick_target`

- FMZ source id: 440810 (lineage).
- Source: https://www.fmz.com/strategy/440810 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 11:38:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C140). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry |
| 2 | ADAPT | Tick target -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_tp` [0.015, 1.0] x `slow` [50, 100]: **4 trials**; SMA 20 and ATR 14 fixed.

## Ambiguities resolved

- na stop places nothing; tick target as an ATR multiple. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

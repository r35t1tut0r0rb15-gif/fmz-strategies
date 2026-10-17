# #431494 基于SMA交叉策略SMA-Crossover-Strategy -> `fmz_431494_sma_7_25_cross`

- FMZ source id: 431494 (lineage).
- Source: https://www.fmz.com/strategy/431494 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-08 11:36:51). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [7, 14] x `slow` [25, 50]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

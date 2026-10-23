# #434579 双重优化组合反转EMA加权交易策略Comb-Reverse-EMA-Volume-Weighting-Optimization-Trading-Strategies -> `fmz_434579_reversal123_vwema22_combo_reversal`

- FMZ source id: 434579 (lineage).
- Source: https://www.fmz.com/strategy/434579 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-07 16:39:50). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Combined price-pattern and volume-weighted EMA states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_vw` [22, 50] x `length` [14, 9]: **4 trials**; K smoothing 1, D 3, level 50.

## Ambiguities resolved

- Volume = broker tick volume (VWEMA). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "hpotter_combo"`.

## Marks

`none`

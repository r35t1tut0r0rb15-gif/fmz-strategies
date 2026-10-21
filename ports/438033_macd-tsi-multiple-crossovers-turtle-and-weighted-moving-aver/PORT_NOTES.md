# #438033 多重交叉海龟与加权移动平均线与MACD与TSI组合策略Multiple-Crossovers-Turtle-and-Weighted-Moving-Average-and-MACD-and-TSI-Combination-Strategy -> `fmz_438033_quad_hull_macd_tsi_multicross`

- FMZ source id: 438033 (lineage).
- Source: https://www.fmz.com/strategy/438033 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-08 14:19:02). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull-style averages, MACD and TSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG438033. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`keh` [7, 14] x `teh` [14, 28]: **4 trials**; VWMA 1, MACD 7 / 14 / 3 and TSI 5 / 3 / 2 at +-4 fixed.

## Ambiguities resolved

- vwma(close, 1) = close; entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

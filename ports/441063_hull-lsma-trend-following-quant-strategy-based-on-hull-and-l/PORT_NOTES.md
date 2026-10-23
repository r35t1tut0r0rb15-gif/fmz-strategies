# #441063 基于Hull指标和LSMA指标的趋势跟踪量化策略Trend-Following-Quant-Strategy-Based-on-Hull-and-LSMA-Indicators -> `fmz_441063_lsma25_cross_hull55_counter_slope_3m_reversal`

- FMZ source id: 441063 (lineage).
- Source: https://www.fmz.com/strategy/441063 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 11:58:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed 100 % target from the fill |
| 2 | PASS | LSMA crossings of the Hull MA against its slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity, contracts = equity / close x leverage, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hull_len` [55, 100] x `lsma_len` [25, 50]: **4 trials**; target 100 %.

## Ambiguities resolved

- 100 % targets kept, 999 % stop dropped. Volume not used. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`

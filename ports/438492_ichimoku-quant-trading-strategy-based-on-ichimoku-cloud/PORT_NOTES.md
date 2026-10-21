# #438492 基于Ichimoku云图的量化交易策略Quant-Trading-Strategy-Based-on-Ichimoku-Cloud -> `fmz_438492_close_cross_span_a_span_b_side`

- FMZ source id: 438492 (lineage).
- Source: https://www.fmz.com/strategy/438492 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 14:20:43). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C111). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku spans |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [9, 7] x `base` [26, 22]: **4 trials**; span B 52 fixed.

## Ambiguities resolved

- Current spans; the trailing exit is never armed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`

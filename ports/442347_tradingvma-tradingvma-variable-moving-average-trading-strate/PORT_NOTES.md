# #442347 可变移动平均线-TradingVMA-策略TradingVMA-Variable-Moving-Average-Trading-Strategy -> `fmz_442347_variable_ma_direction_reversal`

- FMZ source id: 442347 (lineage).
- Source: https://www.fmz.com/strategy/442347 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 11:47:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | VMA direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10]: **2 trials**.

## Ambiguities resolved

- Date window dropped (BUY read as long). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`none`

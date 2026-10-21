# #438931 基于EMA-MA交叉的交易策略EMA-MA-Crossover-Options-Trading-Strategy -> `fmz_438931_ema50_100_cross`

- FMZ source id: 438931 (lineage).
- Source: https://www.fmz.com/strategy/438931 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-16 14:14:42). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG438931. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema1` [50, 20] x `ema2` [100, 200]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

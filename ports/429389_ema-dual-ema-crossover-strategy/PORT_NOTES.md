# #429389 双EMA金叉死叉策略Dual-EMA-Crossover-Strategy -> `fmz_429389_ema3_9_cross_long`

- FMZ source id: 429389 (lineage).
- Source: https://www.fmz.com/strategy/429389 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-16 16:15:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C24). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average crosses only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and the off-by-default stops stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429389. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 5] x `slow` [9, 21]: **4 trials**.

## Ambiguities resolved

- Off-by-default shorts and stops not ported. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

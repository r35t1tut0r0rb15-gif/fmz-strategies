# #429085 双TEMA叉死叉交易策略Dual-TEMA-Crossover-Trading-Strategy -> `fmz_429085_tema_20_60_long`

- FMZ source id: 429085 (lineage).
- Source: https://www.fmz.com/strategy/429085 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-12 17:34:19). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() capital and 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [60, 100]: **4 trials**.

## Ambiguities resolved

- Long only (shorts commented out). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

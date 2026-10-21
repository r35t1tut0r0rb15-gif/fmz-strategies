# #437675 动向指标与-Hull-平均线组合策略DMI-and-HMA-Combination-Strategy -> `fmz_437675_di_cross_hull_net_order`

- FMZ source id: 437675 (lineage).
- Source: https://www.fmz.com/strategy/437675 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 17:23:06). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Directional indicators and Hull averages |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, pyramiding and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hull_len1` [29, 15] x `di_len` [76, 30]: **4 trials**; Hull 2 fixed.

## Ambiguities resolved

- strategy.order by its net effect (one step per order); nz-seeded DI sums. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`

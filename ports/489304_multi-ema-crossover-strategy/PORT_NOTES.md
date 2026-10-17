# #489304 多重指数移动平均线交叉策略-Multi-EMA-Crossover-Strategy -> `fmz_489304_four_ema_pair_crosses_net_long`

- FMZ source id: 489304 (lineage).
- Source: https://www.fmz.com/strategy/489304 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-03 11:46:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMAs only |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 25 % per entry and pyramiding 4 quoted (adds not ported). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`GRID = {}`: **1 trial** (the four EMA pairs are fixed in the source; no inputs).

## Ambiguities resolved

- Four named sub-entries under pyramiding 4 are adds (sizing): the port is long while any sub-position is open.
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

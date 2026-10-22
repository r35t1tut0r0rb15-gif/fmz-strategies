# #473937 Dynamic-Support-Resistance-Price-Action-Trading-System-动态支阻价格行为交易系统 -> `fmz_473937_range_edge_candle_patterns_avg_bracket_from_flat`

- FMZ source id: 473937 (lineage).
- Source: https://www.fmz.com/strategy/473937 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-04 15:19:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the average-price bracket as fixed fractions |
| 2 | PASS | Range-edge candle patterns with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [16, 32] x `sensitivity` [0.018, 0.005]: **4 trials**; the bracket 16 % / 9.5 %.

## Ambiguities resolved

- The short wins a bar with both setups (call order). Entries only from flat.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

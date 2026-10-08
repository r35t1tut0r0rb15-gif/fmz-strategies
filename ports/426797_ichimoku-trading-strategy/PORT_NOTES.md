# #426797 Ichimoku Trading Strategy -> `fmz_426797_doubled_ichimoku_long`

- Source: https://www.fmz.com/strategy/426797 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 16:13:33). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conv` [9, 20] x `base` [26, 60] x `span_b` [52, 120] x `disp` [26, 30]: **16 trials**, defaults 20 / 60 / 120 / 30 (the source's).

## Ambiguities resolved

- `position_count = 1 / 0` inside the if-blocks declare locals (= not :=): the var never blocks an entry (as written).
- Same bar: from flat the entry stands; while long the close goes flat. Stop-loss input unused.
- Long only. FREQ = "2h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks (2026-10-07)

`none`

# #442635 带滑点止损的DCA定投策略DCA-Strategy-with-Trailing-Take-Profit -> `fmz_442635_dip_reference_close_trail_take_profit_long`

- FMZ source id: 442635 (lineage).
- Source: https://www.fmz.com/strategy/442635 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 14:01:20). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Buy-the-dip reference with a close-based trailing take-profit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [0.6, 2.0] x `trail_pct` [0.1, 0.5]: **4 trials**; the deviation and the count limit fixed.

## Ambiguities resolved

- One long at a time (default pyramiding); refused buys still move the reference. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

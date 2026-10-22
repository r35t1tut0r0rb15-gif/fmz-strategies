# #488536 Dynamic Liquidity Driven Market Structure Adaptive Trading Strategy -> `fmz_488536_liquidity_touch_internal_shift_tick_close_exits_flat`

- FMZ source id: 488536 (lineage).
- Source: https://www.fmz.com/strategy/488536 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:13:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based tick stop and target |
| 2 | ADAPT | Tick distances read as percents at the header price |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [10, 20] x `stop_ticks` [10, 100]: **4 trials** (target 2 x the stop); ticks at 0.01 / 3000 of the price.

## Ambiguities resolved

- The state loop is as written; ticks read at ETH 3000 on closes. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "market_structure"`.

## Marks

`none`

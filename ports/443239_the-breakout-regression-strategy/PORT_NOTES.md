# #443239 The Breakout Regression Strategy -> `fmz_443239_quiet_range_close_breakout_ten_bar_exit`

- FMZ source id: 443239 (lineage).
- Source: https://www.fmz.com/strategy/443239 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-01 11:58:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Closing breakouts with a range filter; bar-count exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`high_lookback` [9, 20] x `exit_after` [10, 5]: **4 trials**; the 50-bar low and the range filter fixed.

## Ambiguities resolved

- Bar-count exits from the fill bar. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`

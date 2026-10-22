# #441092 Breakout Reversal Strategy with Stop Loss -> `fmz_441092_close_high_100_breakout_25_bar_exit_long`

- FMZ source id: 441092 (lineage).
- Source: https://www.fmz.com/strategy/441092 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 14:56:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Closing-high breakout and bar count |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`breakout_period` [100, 50] x `hold_bars` [25, 10]: **4 trials**.

## Ambiguities resolved

- Bar count from the latest signal. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`

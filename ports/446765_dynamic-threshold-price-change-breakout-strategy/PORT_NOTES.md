# #446765 Dynamic Threshold Price Change Breakout Strategy -> `fmz_446765_ten_pct_day_up_long_swing_low_test`

- FMZ source id: 446765 (lineage).
- Source: https://www.fmz.com/strategy/446765 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-01 12:03:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop is a close-time test |
| 2 | PASS | Large daily moves with a swing-low test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`change` [0.1, 0.05] x `stop_len` [6, 10]: **4 trials**.

## Ambiguities resolved

- Close-time stop test; script's state flag. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`

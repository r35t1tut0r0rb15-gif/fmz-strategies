# #437746 Breakthrough Tracking Strategy -> `fmz_437746_guarded_hh_ll_breakout`

- FMZ source id: 437746 (lineage).
- Source: https://www.fmz.com/strategy/437746 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 12:00:25). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG437746. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [26, 50] x `guard` [10, 5]: **4 trials**; guard offset 1 fixed.

## Ambiguities resolved

- Both extremes read one bar back, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`

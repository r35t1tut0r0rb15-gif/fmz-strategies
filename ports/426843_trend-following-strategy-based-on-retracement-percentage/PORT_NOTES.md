# #426843 Trend Following Strategy Based on Retracement Percentage -> `fmz_426843_dip_from_high_long`

- Source: https://www.fmz.com/strategy/426843 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 19:49:14). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick-scaled target -> fraction of the fill price, as meant. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`range_of_tops` [60, 90, 120] x `take_profit_percent` [6, 10]: **6 trials**, defaults 90 / 6 (the source's).

## Ambiguities resolved

- As written the entry uses the take-profit percent, not the 3 % retrace input (decision owed: likely a slip).
- Target in ticks x basis_points 100 is 6 % only on a 0.01 tick; ported as meant (tp_stop 6 % of the fill).
- Entries need flat: simulate() mirrors the target. Long only.
- Daily bars are broker days; target on daily bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks (2026-10-07)

`coarse_bar_stop`

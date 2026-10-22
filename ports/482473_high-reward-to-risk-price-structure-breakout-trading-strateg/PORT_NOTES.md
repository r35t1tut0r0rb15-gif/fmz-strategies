# #482473 High Reward to Risk Price Structure Breakout Trading Strategy -> `fmz_482473_hh20_ll20_close_break_swing10_stop_5r_reversal`

- FMZ source id: 482473 (lineage).
- Source: https://www.fmz.com/strategy/482473 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 15:42:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing stop and R-multiple target as fractions of the fill |
| 2 | PASS | Donchian-style breakouts with a swing stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG482473. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 50] x `rr_multiplier` [5.0, 2.0]: **4 trials**; stop lookback 10.

## Ambiguities resolved

- The per-day trade limit never binds, as written. A repeat breakout's re-sent bracket is pending.
- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

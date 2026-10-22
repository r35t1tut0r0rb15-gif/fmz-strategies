# #441160 Richards Turtle Trading Strategy -> `fmz_441160_turtle_close_channel_flag_state`

- FMZ source id: 441160 (lineage).
- Source: https://www.fmz.com/strategy/441160 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-06 11:56:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Closing-price channels and the ATR stop test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `stop_mult` [4, 2]: **4 trials**; ATR 20 fixed.

## Ambiguities resolved

- Short-side flag cleared on its own bar, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`

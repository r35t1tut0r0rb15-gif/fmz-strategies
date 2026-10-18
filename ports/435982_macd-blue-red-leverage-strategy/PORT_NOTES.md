# #435982 Macd Blue Red Leverage Strategy -> `fmz_435982_elder_impulse_colours`

- FMZ source id: 435982 (lineage).
- Source: https://www.fmz.com/strategy/435982 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-20 15:51:37). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Slope and histogram colours |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ema` [13, 21] x `fast` [12, 8]: **4 trials**; slow 26 and signal 9 fixed.

## Ambiguities resolved

- Position follows the colour; blue is flat. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`

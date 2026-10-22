# #484096 Dynamic Color Threshold Volatility Analysis Trading Strategy -> `fmz_484096_colour_code_candle_change_tick_bracket_reversal`

- FMZ source id: 484096 (lineage).
- Source: https://www.fmz.com/strategy/484096 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 09:59:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; tick bracket as fractions of the fill |
| 2 | ADAPT | Tick bracket read as fractions at ETH 3000 |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_frac` [6.667e-05, 0.01] x `threshold_percent` [1.0, 5.0]: **4 trials**; target 2 x stop.

## Ambiguities resolved

- The tick bracket is read at ETH 3000. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`coarse_bar_stop`

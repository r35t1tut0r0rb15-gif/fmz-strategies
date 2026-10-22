# #439872 Contrarian Donchian Channel Touch Entry Strategy with Post Stop Loss Pause and Trailing Stop Loss -> `fmz_439872_contrarian_donchian_touch_pause`

- FMZ source id: 439872 (lineage).
- Source: https://www.fmz.com/strategy/439872 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-24 15:07:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C126). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket fixed from the fill; the short's wrong-side levels read as a close |
| 2 | PASS | Donchian touches and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `sl` [0.0022, 0.01]: **4 trials**; risk / reward 2 and the 3-bar pause fixed.

## Ambiguities resolved

- Long bracket from the fill (centre raise pending); one-bar shorts as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

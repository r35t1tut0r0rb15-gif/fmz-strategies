# #488541 Dynamic Bollinger Bands Breakout Trend Tracking Strategy -> `fmz_488541_bb20_2_breakout_tp5_sl2_reversal`

- FMZ source id: 488541 (lineage).
- Source: https://www.fmz.com/strategy/488541 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:24:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C267). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Bollinger breakouts with a percent bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`takeProfitPerc` [5.0, 3.0] x `stopLossPerc` [2.0, 1.0]: **4 trials**; BB 20 / 2.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`

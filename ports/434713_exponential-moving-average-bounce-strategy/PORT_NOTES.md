# #434713 Exponential Moving Average Bounce Strategy -> `fmz_434713_ema_bounce_swing_bracket`

- FMZ source id: 434713 (lineage).
- Source: https://www.fmz.com/strategy/434713 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-08 16:47:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C71). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (approximation stated) |
| 2 | PASS | Average bounces and swing-based exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50] x `rr` [1.2, 2.0]: **4 trials**; swing 10 and the 0.2 % increment fixed.

## Ambiguities resolved

- Swing level from the signal bar (the script's is from the fill bar). Flat tracked through the bracket. Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop`

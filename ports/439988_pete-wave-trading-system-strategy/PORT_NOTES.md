# #439988 Pete Wave Trading System Strategy -> `fmz_439988_pete_wave_sma9_22_breakout_stop`

- FMZ source id: 439988 (lineage).
- Source: https://www.fmz.com/strategy/439988 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-25 15:36:16). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C128). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent stop from the fill |
| 2 | ADAPT | Price-unit filters -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent and point inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trailing_stop` [1.5, 3.0] x `step_frac` [1.19e-05, 0.001]: **4 trials**; SMA 9 / 22 and the 9-bar breakout fixed.

## Ambiguities resolved

- Price-unit filters as fractions; pullback branch never passes, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

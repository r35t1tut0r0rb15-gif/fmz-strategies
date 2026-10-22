# #484101 Multi Dimensional Chart Pattern Quantitative Strategy A Technical Analysis Trading System Integrating Head and Shoulders and Double Top Bottom Formations -> `fmz_484101_five_bar_double_top_bottom_candle_atr1_5_3_bracket_reversal`

- FMZ source id: 484101 (lineage).
- Source: https://www.fmz.com/strategy/484101 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-28 10:19:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C261). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | Five-bar double tops / bottoms with an ATR bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_length` [14, 20] x `tp_atr` [3.0, 2.0]: **4 trials**; stop 1.5 ATR.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "reversal_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

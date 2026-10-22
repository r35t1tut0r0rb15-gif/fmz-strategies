# #477956 Enhanced Price Volume Trend Momentum Strategy -> `fmz_477956_macd_hist_colour_turn_atr_bracket_reversal`

- FMZ source id: 477956 (lineage).
- Source: https://www.fmz.com/strategy/477956 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 15:40:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | MACD histogram colour turns with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [10, 3] x `sl_atr` [3, 1]: **4 trials**; MACD 12 / 26 / 9, ATR 14.

## Ambiguities resolved

- The short signal is a rising positive histogram, as written. Repeat-signal re-sends not followed.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

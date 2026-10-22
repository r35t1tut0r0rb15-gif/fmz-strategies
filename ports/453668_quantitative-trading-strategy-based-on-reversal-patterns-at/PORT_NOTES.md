# #453668 Quantitative Trading Strategy Based on Reversal Patterns at Support and Resistance Levels -> `fmz_453668_reversal_candles_at_50bar_extremes_bracket_reversal`

- FMZ source id: 453668 (lineage).
- Source: https://www.fmz.com/strategy/453668 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-07 16:45:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C193). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal-bar levels as fractions; re-issued levels pending (mark) |
| 2 | PASS | Reversal candles at range extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [50, 20] x `sl_pct` [0.01, 0.02] x `tp_pct` [0.03, 0.05]: **8 trials**; the tolerance fixed.

## Ambiguities resolved

- isEngulfing is the bearish test only; re-issued levels pending. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

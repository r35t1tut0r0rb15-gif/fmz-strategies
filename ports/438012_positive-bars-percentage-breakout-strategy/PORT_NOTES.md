# #438012 Positive Bars Percentage Breakout Strategy -> `fmz_438012_positive_bars_pct_atr_bracket`

- FMZ source id: 438012 (lineage).
- Source: https://www.fmz.com/strategy/438012 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-08 10:32:25). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Green-bar share and ATR distances |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438012. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [13, 26] x `k_atr` [10.0, 5.0]: **4 trials**; 70 / 30, ATR 14 and the 1.6 ratio fixed.

## Ambiguities resolved

- ATR stop from the signal bar instead of the fill bar (known at the fill's open). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`

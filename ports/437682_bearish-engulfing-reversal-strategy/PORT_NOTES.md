# #437682 Bearish Engulfing Reversal Strategy -> `fmz_437682_bearish_engulfing_short_state`

- FMZ source id: 437682 (lineage).
- Source: https://www.fmz.com/strategy/437682 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-04 17:35:18). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C104). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; levels tested at bar closes |
| 2 | ADAPT | Price-unit distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND432977. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [0.13, 1.0] x `atr_len` [14, 28]: **4 trials**; target 2 x and minimum body 0.1 x the stop distance.

## Ambiguities resolved

- Price units -> ATR multiples; exit one bar after the touch. Short only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

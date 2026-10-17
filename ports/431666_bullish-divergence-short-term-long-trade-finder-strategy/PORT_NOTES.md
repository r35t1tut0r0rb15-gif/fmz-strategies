# #431666 Bullish Divergence Short term Long Trade Finder Strategy -> `fmz_431666_rsi_bull_divergence_long`

- FMZ source id: 431666 (lineage).
- Source: https://www.fmz.com/strategy/431666 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-10 11:37:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits |
| 2 | PASS | RSI pivots, price lows and a percentage stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pivot_left` [25, 10] x `stop_pct` [5, 2]: **4 trials**; RSI 14, right 5, the range 5-50 and the RSI lines fixed.

## Ambiguities resolved

- Confirmation-bar readings as written; hourly RSI from completed hours. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_divergence"`.

## Marks

`none`

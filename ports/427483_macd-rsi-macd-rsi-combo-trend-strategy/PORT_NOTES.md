# #427483 MACD-RSI Combo Trend Strategy -> `fmz_427483_macd_rsi_same_bar_cross`

- FMZ source id: 427483 (lineage).
- Source: https://www.fmz.com/strategy/427483 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 15:40:02). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator crosses. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`over_bought` [70, 60] x `over_sold` [30, 40] x `rsi_length` [14, 9]: **8 trials**; defaults 70 / 30 / 14 (the source's); MACD 12 / 26 / 9 fixed.

## Ambiguities resolved

- Both crosses on the same bar, as written. REVERSAL INTENDED. FREQ = "6h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`

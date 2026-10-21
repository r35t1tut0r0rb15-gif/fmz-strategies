# #436992 Three Inside Down Reversal Strategy -> `fmz_436992_three_inside_down_long_state`

- FMZ source id: 436992 (lineage).
- Source: https://www.fmz.com/strategy/436992 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-29 11:09:56). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; levels tested at bar closes |
| 2 | ADAPT | Price-unit distances -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [0.13, 1.0] x `atr_len` [14, 28]: **4 trials**; the target is 2 x the stop distance.

## Ambiguities resolved

- Bearish pattern traded long as written; price units -> ATR multiples; exit one bar after the touch. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`

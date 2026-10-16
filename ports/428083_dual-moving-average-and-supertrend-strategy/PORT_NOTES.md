# #428083 Dual Moving Average and Supertrend Strategy -> `fmz_428083_ema_trend_long`

- FMZ source id: 428083 (lineage).
- Source: https://www.fmz.com/strategy/428083 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 15:12:50). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMA lengths only. |
| 3 | PASS | Spot pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len1` [21, 13] x `len2` [55, 34]: **4 trials**; defaults 21 / 55 (the source's); EMA 233 fixed.

## Ambiguities resolved

- SuperTrend, EMA 200 and the short conditions reach no order. Operator precedence as written (the cross alone enters).
- A same-bar close acts only on an open position. Long only. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

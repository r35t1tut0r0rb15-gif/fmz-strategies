# #432657 Double Strong Indicators Strategy -> `fmz_432657_macd_cross_after_rsi_extreme`

- FMZ source id: 432657 (lineage).
- Source: https://www.fmz.com/strategy/432657 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-20 09:47:41). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C53). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crosses and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432657. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`oversold` [35, 30] x `overbought` [80, 70]: **4 trials**; MACD 12 / 26 / 9, RSI 14 and the six-bar memory fixed.

## Ambiguities resolved

- Cross flags read as true on a cross. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`

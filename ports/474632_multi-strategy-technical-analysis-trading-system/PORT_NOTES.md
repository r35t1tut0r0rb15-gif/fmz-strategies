# #474632 Multi Strategy Technical Analysis Trading System -> `fmz_474632_macd_hist_three_up_two_down_long`

- FMZ source id: 474632 (lineage).
- Source: https://www.fmz.com/strategy/474632 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 11:06:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram runs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (MACD lengths constants; type MACD).

## Ambiguities resolved

- Strategy type MACD (default); the other types not ported. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`

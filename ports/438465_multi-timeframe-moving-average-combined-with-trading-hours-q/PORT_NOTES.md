# #438465 Multi Timeframe Moving Average Combined with Trading Hours Quantitative Trading Strategy -> `fmz_438465_monday_alma_cross_long`

- FMZ source id: 438465 (lineage).
- Source: https://www.fmz.com/strategy/438465 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 11:50:37). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | ALMA crossings on Mondays; Sunday close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [17, 34] x `ma_type` ["ALMA", "EMA"]: **4 trials**; the 10 % / 30 % bracket fixed.

## Ambiguities resolved

- UTC weekdays; MA type swept over ALMA / EMA; bracket fixed at the fill. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`

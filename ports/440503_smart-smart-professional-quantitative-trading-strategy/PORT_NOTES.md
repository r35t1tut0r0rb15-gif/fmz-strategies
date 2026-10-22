# #440503 SMART专业量化交易策略SMART-Professional-Quantitative-Trading-Strategy -> `fmz_440503_daily_close_direction_flip`

- FMZ source id: 440503 (lineage).
- Source: https://www.fmz.com/strategy/440503 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 10:28:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed days |
| 2 | PASS | Daily close change |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [1, 3]: **2 trials**; days between the compared daily closes.

## Ambiguities resolved

- Daily close from the last completed broker day; one signal a day. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`.

## Marks

`none`

# #449948 Turnaround Tuesday Strategy Weekend Filter -> `fmz_449948_turnaround_tuesday_monday_buy_wednesday_exit_long`

- FMZ source id: 449948 (lineage).
- Source: https://www.fmz.com/strategy/449948 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-30 16:07:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C182). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; filters from the previous bar |
| 2 | PASS | Weekday seasonality with trend, RSI and ATR filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored; the commission is a cost, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_period` [30, 50] x `rsi_max` [51.0, 40.0]: **4 trials**; the ATR filter and the May exclusion fixed.

## Ambiguities resolved

- UTC weekdays; every Monday bar can signal. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`

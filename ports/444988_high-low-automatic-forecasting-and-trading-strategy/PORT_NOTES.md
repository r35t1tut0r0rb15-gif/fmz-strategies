# #444988 High Low Automatic Forecasting and Trading Strategy -> `fmz_444988_0900_utc_bar_range_break_rsi_reversal`

- FMZ source id: 444988 (lineage).
- Source: https://www.fmz.com/strategy/444988 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-15 17:22:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C171). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the range from the completed 09:00 bar |
| 2 | PASS | Breaks of a fixed-hour range with RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG444988. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`session_hour` [9, 13] x `rsi_length` [14, 7]: **4 trials**; the RSI levels fixed.

## Ambiguities resolved

- Range = the 09:00 UTC bar; targets only plot. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`

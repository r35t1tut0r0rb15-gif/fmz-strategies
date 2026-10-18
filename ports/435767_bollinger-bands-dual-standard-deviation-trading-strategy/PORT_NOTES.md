# #435767 Bollinger Bands Dual Standard Deviation Trading Strategy -> `fmz_435767_bollinger_1sd_breakout`

- FMZ source id: 435767 (lineage).
- Source: https://www.fmz.com/strategy/435767 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-18 17:23:42). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger band crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 20, 50]: **3 trials**; the 1 sd width is fixed by the script.

## Ambiguities resolved

- 1 sd bands trade; the 2 sd only draws. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`

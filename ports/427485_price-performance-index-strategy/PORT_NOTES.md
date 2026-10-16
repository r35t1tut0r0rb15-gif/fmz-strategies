# #427485 Price Performance Index Strategy -> `fmz_427485_hpotter_performance_index`

- FMZ source id: 427485 (lineage).
- Source: https://www.fmz.com/strategy/427485 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 16:19:31). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Rate of change. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [14, 7, 28]: **3 trials**; default 14 (the source's).

## Ambiguities resolved

- Broker-day bars. REVERSAL INTENDED. FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "slope_momentum"`.

## Marks

`none`

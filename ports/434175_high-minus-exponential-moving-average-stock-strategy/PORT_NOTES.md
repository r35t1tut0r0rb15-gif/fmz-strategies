# #434175 High Minus Exponential Moving Average Stock Strategy -> `fmz_434175_high_minus_ema_state`

- FMZ source id: 434175 (lineage).
- Source: https://www.fmz.com/strategy/434175 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-04 14:29:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C65). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | The high against an average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND433079. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [13, 26, 50]: **3 trials**.

## Ambiguities resolved

- One-bar-back reads as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

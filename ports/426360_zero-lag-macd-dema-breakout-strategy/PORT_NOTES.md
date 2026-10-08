# #426360 Zero Lag MACD DEMA Breakout Strategy -> `fmz_426360_zero_lag_macd_sign`

- Source: https://www.fmz.com/strategy/426360 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-11 14:43:52). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 12] x `slow` [26, 40]: **4 trials**, defaults 12 / 26 (the source's).

## Ambiguities resolved

- The signal-line DEMA only plots; orders read the sign of the zero-lag MACD line.
- The test-period window is always true.
- Daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks (2026-10-07)

`none`

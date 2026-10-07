# #365128 SuperTrended Moving Averages -> `fmz_365128_supertrended_ema`

- Source: https://www.fmz.com/strategy/365128 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-24 10:14:59). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A12). Not run.

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

`length` [50, 100, 200] x `mult` [0.5, 1.0, 2.0] = **9 trials**. ATR period 10 stays at the original.

## Ambiguities resolved

- MA type default EMA; bands are around the MA instead of hl2.
- Classic SuperTrend recursion, trend starts at 1.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`

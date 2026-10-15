# #427274 Zero-Lag Hull EMA Combo Trend Following Strategy -> `fmz_427274_ujanja_zero_lag_hull`

- FMZ source id: 427274 (lineage).
- Source: https://www.fmz.com/strategy/427274 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-19 16:53:31). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [30, 15, 60] x `s_period` [176, 88]: **6 trials**; defaults 30 / 176 (the source's).

## Ambiguities resolved

- The short condition is `not long`, so the script is short from its first bar while the averages are still undefined; ported as written.
- WMA weights 1..n; the Hull lengths follow `round()` of the smoother.
- Always in the market (REVERSAL INTENDED). FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

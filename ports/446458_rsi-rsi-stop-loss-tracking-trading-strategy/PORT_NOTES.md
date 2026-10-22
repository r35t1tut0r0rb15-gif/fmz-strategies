# #446458 RSI止损追踪交易策略-RSI-Stop-Loss-Tracking-Trading-Strategy -> `fmz_446458_rsi14_cross_under_30_close_stop_long`

- FMZ source id: 446458 (lineage).
- Source: https://www.fmz.com/strategy/446458 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-28 17:56:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C174). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop is a close test at the bar close |
| 2 | PASS | RSI cross-down with a close-based stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`threshold` [30, 25] x `stop_pct` [1.5, 3.0]: **4 trials**; the RSI length fixed.

## Ambiguities resolved

- Close-test stop re-based on each signal. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

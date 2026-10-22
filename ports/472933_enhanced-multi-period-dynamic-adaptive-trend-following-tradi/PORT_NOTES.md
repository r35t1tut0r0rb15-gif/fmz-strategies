# #472933 Enhanced Multi Period Dynamic Adaptive Trend Following Trading System -> `fmz_472933_ema9_21_cross_rsi_adx15_filter_long`

- FMZ source id: 472933 (lineage).
- Source: https://www.fmz.com/strategy/472933 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-25 10:58:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C212). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the bracket armed only by a repeat signal not ported (mark) |
| 2 | PASS | EMA crossings with RSI and ADX filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND471697. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50] x `adx_th` [15, 20]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Same rules as #471697 (ADX 15); repeat-signal bracket not ported (trailing_stop_pending). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

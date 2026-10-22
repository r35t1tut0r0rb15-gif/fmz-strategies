# #476265 Dynamic Moving Average Trend Following with RSI Confirmation Trading Strategy -> `fmz_476265_ema9_21_cross_rsi50_reversal`

- FMZ source id: 476265 (lineage).
- Source: https://www.fmz.com/strategy/476265 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 15:31:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C231). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with an RSI 50 filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the drawn stop percentage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; RSI 14 / 50.

## Ambiguities resolved

- The stop is drawn only, no order. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`

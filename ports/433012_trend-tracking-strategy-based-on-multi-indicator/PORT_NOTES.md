# #433012 Trend Tracking Strategy Based on Multi indicator -> `fmz_433012_inverted_band_rsi_cross`

- FMZ source id: 433012 (lineage).
- Source: https://www.fmz.com/strategy/433012 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-23 15:43:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band, average and RSI crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [5, 10] x `mult` [1.5, 2.0]: **4 trials**; RSI 7 / 25 / 75 and the averages fixed.

## Ambiguities resolved

- Long on the bearish pattern, short on the bullish one, and the level inputs as RSI lengths, all as written; entry wins over a same-bar close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`

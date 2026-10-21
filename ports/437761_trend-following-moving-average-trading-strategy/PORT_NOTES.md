# #437761 Trend Following Moving Average Trading Strategy -> `fmz_437761_smoothed_extreme_atr_bands`

- FMZ source id: 437761 (lineage).
- Source: https://www.fmz.com/strategy/437761 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-05 13:48:07). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C105). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed extremes with ATR offsets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [200, 100] x `atr_mult` [2.0, 3.0]: **4 trials**; both lengths and averages swept together; ATR 14 fixed.

## Ambiguities resolved

- Call-order fills. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`

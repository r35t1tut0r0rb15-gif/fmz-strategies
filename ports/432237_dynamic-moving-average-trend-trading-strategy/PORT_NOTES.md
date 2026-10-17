# #432237 Dynamic Moving Average Trend Trading Strategy -> `fmz_432237_smoothed_waddah_long`

- FMZ source id: 432237 (lineage).
- Source: https://www.fmz.com/strategy/432237 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-15 17:45:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C50). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD change against the band width, RSI level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sensitivity` [150, 75] x `rsi_filter` [40, 50]: **4 trials**; MACD 20 / 40 and the bands 20 x 1.5 fixed.

## Ambiguities resolved

- Heikin Ashi close = ohlc4 of the bar. The close's second argument read as when. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`

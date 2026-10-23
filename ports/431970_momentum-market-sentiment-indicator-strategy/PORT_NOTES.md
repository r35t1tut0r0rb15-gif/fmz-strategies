# #431970 Momentum Market Sentiment Indicator Strategy -> `fmz_431970_change_per_volume_sentiment_macd_hist_zero_long`

- FMZ source id: 431970 (lineage).
- Source: https://www.fmz.com/strategy/431970 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 17:51:20). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD of a price-change-per-volume ratio |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 100, commission 0.08 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ema` [40, 20] x `slow_ema` [204, 100]: **4 trials**; lookback 49, signal 20.

## Ambiguities resolved

- Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_oscillator"`.

## Marks

`none`

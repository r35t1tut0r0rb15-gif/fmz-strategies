# #361332 Sentiment Oscillator -> `fmz_361332_change_per_volume_sentiment_macd_hist_zero_long`

- FMZ source id: 361332 (lineage).
- Source: https://www.fmz.com/strategy/361332 (PineScript v4, author 发明者量化, FMZ last
  modified 2022-05-05 20:45:11). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD of a price-change / volume sentiment line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ms_len` [49, 20] x `ema_len2` [204, 100]: **4 trials**; fast 40, signal 20.

## Ambiguities resolved

- Volume = broker tick volume (a level divisor: its scale differs by broker). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`

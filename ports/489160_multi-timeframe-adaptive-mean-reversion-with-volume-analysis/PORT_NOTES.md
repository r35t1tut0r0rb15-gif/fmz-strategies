# #489160 Multi Timeframe Adaptive Mean Reversion with Volume Analysis Strategy -> `fmz_489160_bollinger_mean_reversion_volume_daily_sma_trend_1h_reversal`

- FMZ source id: 489160 (lineage).
- Source: https://www.fmz.com/strategy/489160 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-02 11:39:54). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger mean reversion on volume, filtered by the daily trend and volatility |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [2.0, 2.5] x `vol_threshold` [1.5, 2.0]: **4 trials**; MA 20, RSI 14, ATR 14 < 3 %, daily SMA 20.

## Ambiguities resolved

- Daily SMA of the last completed broker day. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

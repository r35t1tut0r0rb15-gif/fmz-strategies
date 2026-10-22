# #446465 布林带与RSI交易策略-Bollinger-Bands-and-RSI-Trading-Strategy -> `fmz_446465_lower_band_rsi_spaced_long`

- FMZ source id: 446465 (lineage).
- Source: https://www.fmz.com/strategy/446465 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-28 18:11:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C175). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Lower-band RSI entries spaced by bars, upper-band RSI exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_interval` [5, 10] x `rsi_lower` [30, 25]: **4 trials**; the band and the upper level fixed.

## Ambiguities resolved

- Spacing counts every buy signal. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

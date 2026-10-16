# #430544 Multi Indicator Bitcoin Daily Trading Strategy -> `fmz_430544_btc_daily_macd_rsi_srsi`

- FMZ source id: 430544 (lineage).
- Source: https://www.fmz.com/strategy/430544 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-30 10:37:58). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a fixed percentage stop. |
| 2 | ADAPT | The price-unit thresholds -> ATR fractions. |
| 3 | PASS | "Bitcoin" in the corpus title only; exchange pair in the header. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_threshold` [30, 20] x `srsi_threshold` [57, 50]: **4 trials**; MACD 11 / 18 / 6, SMA 14, ATR-scaled levels and 5 % stops
fixed.

## Ambiguities resolved

- Price-unit thresholds -> ATR fractions. Both signals on one bar: the short wins. Mark coarse_bar_stop.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`

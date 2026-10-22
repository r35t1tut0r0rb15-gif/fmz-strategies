# #483020 动量背离趋势反转量化策略基于MACD柱状图-Momentum-Divergence-Trend-Reversal-Quantitative-Strategy-Based-on-MACD-Histogram -> `fmz_483020_macd_hist_fade_bigger_candle_contrarian_reversal`

- FMZ source id: 483020 (lineage).
- Source: https://www.fmz.com/strategy/483020 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 09:25:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C254). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram fades against a bigger candle |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_length` [12, 8] x `signal_length` [9, 5]: **4 trials**; MACD slow 26.

## Ambiguities resolved

- REVERSAL INTENDED, no other exit. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`

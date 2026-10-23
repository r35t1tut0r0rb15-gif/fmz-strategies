# #482776 基于布林带和MACD指标的高频交易策略分析系统-High-Frequency-Trading-Strategy-Analysis-System-Based-on-Bollinger-Bands-and-MACD-Indicators -> `fmz_482776_bollinger_bounce_macd_volume_daily_cap_2_4pct_1h_reversal`

- FMZ source id: 482776 (lineage).
- Source: https://www.fmz.com/strategy/482776 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 17:55:49). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 2 % / 4 % bracket from the fill |
| 2 | PASS | Bollinger re-entries with MACD and volume confirmation, daily signal cap |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 5 % of equity, capital, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.02, 0.03] x `tp` [0.04, 0.06]: **4 trials**; BB 20 x 2, MACD 12 / 26 / 9, cap 5 a day.

## Ambiguities resolved

- Bracket from the fill (source: from the bar after). Daily cap on broker days. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`

# #483101 高级量化交易策略多维度指标融合的超级趋势ATR动态跟踪系统-Advanced-Quantitative-Trading-Strategy-Multi-Dimensional-Super-Trend-ATR-Dynamic-Tracking-System -> `fmz_483101_supertrend_macd_adx_volume_divergence_atr_stop_1h_reversal`

- FMZ source id: 483101 (lineage).
- Source: https://www.fmz.com/strategy/483101 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 13:34:24). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop at the signal close as a fraction of the fill |
| 2 | PASS | Supertrend trend entries with MACD / ADX / volume filters and a divergence switch |
| 3 | PASS | Exchange pair in the header only (ETH named in the title). |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.5, 4.0] x `stop_mult` [2.2, 3.0]: **4 trials**; ATR 8, MACD 10 / 21 / 7, ADX 18 > 28, volume x 1.8.

## Ambiguities resolved

- Stop fixed at the first signal; repeats re-send it (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`

# #440465 多周期MACD指标交易策略Multi-Timeframe-MACD-Trading-Strategy -> `fmz_440465_macd_hist_ema50_sar_atr_exits`

- FMZ source id: 440465 (lineage).
- Source: https://www.fmz.com/strategy/440465 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 17:44:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bar-tested SAR and band exits |
| 2 | PASS | MACD histogram, EMA, SAR and ATR band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent of equity, capital and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [50, 100] x `bse` [10, 20]: **4 trials**; MACD, SAR and ATR settings fixed.

## Ambiguities resolved

- Timed exit on the sign of the open profit (close against the fill). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`

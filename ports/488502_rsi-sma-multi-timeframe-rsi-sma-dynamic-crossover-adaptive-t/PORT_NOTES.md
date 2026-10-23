# #488502 多时间周期RSI-SMA动态交叉自适应交易系统-Multi-Timeframe-RSI-SMA-Dynamic-Crossover-Adaptive-Trading-System -> `fmz_488502_rsi_sma_cross_breakout_volume_atr_tiny_target_1h_long_only`

- FMZ source id: 488502 (lineage).
- Source: https://www.fmz.com/strategy/488502 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-28 11:36:12). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | RSI / SMA crossings on breakout bars with volume and trend filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [2.5, 1.5] x `tp_perc` [5.0, 100.0]: **4 trials**; RSI 18, SMA 50, EMA 35 / 100, volume x 1.2.

## Ambiguities resolved

- Target 0.125 ATR as written. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_momentum"`.

## Marks

`none`

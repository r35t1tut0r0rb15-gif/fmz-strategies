# #475601 多重指标波动率交易RSI-EMA-ATR策略-Multi-Indicator-Volatility-Trading-RSI-EMA-ATR-Strategy -> `fmz_475601_ema5_21_rsi_pullback_atr_filter_3m_reversal`

- FMZ source id: 475601 (lineage).
- Source: https://www.fmz.com/strategy/475601 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:47:41). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI pullbacks in an EMA trend with an ATR activity filter |
| 3 | PASS | Exchange pair in the header only (BTCUSDT named in the title). |
| 4 | DONE | Capital and commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_lo` [45.0, 40.0] x `atr_mult` [0.8, 1.0]: **4 trials**; EMA 5 / 21, RSI 14, ATR 14.

## Ambiguities resolved

- Volume filter off by default. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_pullback"`.

## Marks

`none`

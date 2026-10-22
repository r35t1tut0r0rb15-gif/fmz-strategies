# #482879 多指标综合趋势跟踪策略结合ADX动态交易系统-Multi-Indicator-Trend-Following-Strategy-with-ADX-Dynamic-Trading-System -> `fmz_482879_rsi14_30_70_cross_ema20_50_adx20_atr_bracket_reversal`

- FMZ source id: 482879 (lineage).
- Source: https://www.fmz.com/strategy/482879 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 16:20:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | RSI level crossings with an EMA / ADX trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_multiplier` [1.5, 2.5] x `risk_to_reward` [2.0, 1.5]: **4 trials**; EMA 20 / 50, RSI 14 / 30 / 70, ATR 14, ADX 14 over 20.

## Ambiguities resolved

- The hand-built ADX is kept as written. A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`

# #475590 多重技术指标趋势跟踪与动量RSI过滤交易策略-Multi-Technical-Indicator-Trend-Following-Strategy-with-RSI-Momentum-Filter -> `fmz_475590_ema3_6_cross_custom_supertrend_rsi_atr_bracket_reversal`

- FMZ source id: 475590 (lineage).
- Source: https://www.fmz.com/strategy/475590 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:10:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ATR bracket from the fill |
| 2 | PASS | Fast EMA crossings with a supertrend state and RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [3, 5] x `slow` [6, 10]: **4 trials**; ATR 3, RSI 10, multiples fixed.

## Ambiguities resolved

- The custom supertrend as written; the ATR moves pending. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`

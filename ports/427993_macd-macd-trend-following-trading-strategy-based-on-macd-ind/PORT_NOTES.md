# #427993 基于MACD指标的趋势跟踪交易策略MACD-Trend-Following-Trading-Strategy-Based-on-MACD-Indicator -> `fmz_427993_slow_macd_hist_steps_stoch_blend_volume_flags_close_bracket_reversal`

- FMZ source id: 427993 (lineage).
- Source: https://www.fmz.com/strategy/427993 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-27 16:46:38). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop / target |
| 2 | PASS | Slow MACD histogram momentum with stochastic and volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented strategy() (cash 10000, capital 10000) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss` [4.0, 2.0] x `target` [10.0, 5.0]: **4 trials**; MACD 144 / 312 / 108, stochastics as written.

## Ambiguities resolved

- Flags and the no-op short line as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`

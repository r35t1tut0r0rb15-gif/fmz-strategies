# #477595 基于DI指标的动态波动率趋势跟踪策略结合ATR止盈止损体系-Dynamic-Volatility-Adjusted-Trend-Following-Strategy-Based-on-DI-Indicators-with-ATR-Stop-Management -> `fmz_477595_di14_dominance20_sma20_atr_bracket_reversal`

- FMZ source id: 477595 (lineage).
- Source: https://www.fmz.com/strategy/477595 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:18:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | DI dominance with an SMA filter and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`strength` [20, 10] x `tp_mult` [2.5, 4.0]: **4 trials**; DMI 14, SMA 20, ATR 14, stop 1.5 ATR.

## Ambiguities resolved

- Repeat-signal level updates not followed. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_trend"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

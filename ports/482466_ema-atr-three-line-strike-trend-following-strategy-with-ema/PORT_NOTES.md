# #482466 三线突破趋势跟踪策略结合EMA动态过滤和ATR风险管理系统-Three-Line-Strike-Trend-Following-Strategy-with-EMA-Dynamic-Filter-and-ATR-Risk-Management-System -> `fmz_482466_three_line_strike_ema200_atr_2_1_bracket_reversal`

- FMZ source id: 482466 (lineage).
- Source: https://www.fmz.com/strategy/482466 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 15:30:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C245). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | Three-line-strike candles with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and capital stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [200, 100] x `tp_atr` [2.0, 3.0]: **4 trials**; ATR 14, stop 1 ATR.

## Ambiguities resolved

- A repeat signal's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

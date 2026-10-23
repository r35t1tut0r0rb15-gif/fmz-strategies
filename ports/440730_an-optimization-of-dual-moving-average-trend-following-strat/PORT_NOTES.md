# #440730 An Optimization of Dual Moving Average Trend Following Strategy Based on Indicators Combination -> `fmz_440730_sma40_160_trend_daily_sar_filter_atr_stop_4h_reversal`

- FMZ source id: 440730 (lineage).
- Source: https://www.fmz.com/strategy/440730 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-01 15:13:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop from the signal bar as a fraction of the fill |
| 2 | PASS | Dual-SMA trend with a daily SAR filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 2 % / (2 x ATR), commission 0.2 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [40, 20] x `slow` [160, 100]: **4 trials**; SAR 0.02 / 0.02 / 0.2, ATR 14 x 2.

## Ambiguities resolved

- Daily SAR of the last completed broker day; ATR stop from the signal bar. Volume not used. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_state"`.

## Marks

`coarse_bar_stop`

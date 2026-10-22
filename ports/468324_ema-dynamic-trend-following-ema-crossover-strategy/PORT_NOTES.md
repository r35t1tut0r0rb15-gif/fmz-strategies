# #468324 动态趋势跟踪EMA交叉策略-Dynamic-Trend-Following-EMA-Crossover-Strategy -> `fmz_468324_close_cross_ema21_in_ema200_trend_tick_bracket_reversal`

- FMZ source id: 468324 (lineage).
- Source: https://www.fmz.com/strategy/468324 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:41:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | EMA crossings in an EMA trend with trend-change exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [21, 55] x `tp_atr` [0.0055, 2.0] x `sl_atr` [0.003, 1.0]: **8 trials**; the EMA 200 fixed.

## Ambiguities resolved

- 1-minute request = the daily close; ticks as ATR multiples (1D ~1000); no trail (offset only). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`

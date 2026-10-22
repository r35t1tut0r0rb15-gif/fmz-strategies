# #476248 双均线RSI趋势反转交易策略-基于EMA和RSI的动量突破系统-Dual-EMA-RSI-Momentum-Trend-Reversal-Trading-System-A-Momentum-Breakthrough-Strategy-Based-on-EMA-and-RSI-Crossover -> `fmz_476248_ema9_21_cross_rsi50_long`

- FMZ source id: 476248 (lineage).
- Source: https://www.fmz.com/strategy/476248 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 14:23:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C230). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | EMA crossings with an RSI 50 filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; RSI 14 / 50; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket from the latest close kept pending (trailing_stop_pending). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

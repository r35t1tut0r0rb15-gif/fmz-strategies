# #473706 双均线交叉结合RSI动量优化交易策略-Dual-EMA-Crossover-with-RSI-Momentum-Enhanced-Trading-Strategy -> `fmz_473706_ema9_21_cross_rsi_filter_signal_close_bracket_reversal`

- FMZ source id: 473706 (lineage).
- Source: https://www.fmz.com/strategy/473706 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-02 16:20:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an RSI filter and a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.01, 0.02] x `tp_pct` [0.02, 0.04]: **4 trials**; the EMA / RSI settings fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`

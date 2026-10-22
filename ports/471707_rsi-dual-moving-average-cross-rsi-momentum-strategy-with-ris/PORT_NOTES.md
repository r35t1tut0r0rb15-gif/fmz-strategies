# #471707 双均线交叉RSI动量策略与风险收益优化系统-Dual-Moving-Average-Cross-RSI-Momentum-Strategy-with-Risk-Reward-Optimization-System -> `fmz_471707_rsi_pullback_sma9_21_trend_atr_target_from_flat`

- FMZ source id: 471707 (lineage).
- Source: https://www.fmz.com/strategy/471707 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 16:00:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C210). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal-bar target as a fraction of the fill |
| 2 | PASS | RSI pullbacks in the SMA trend with an ATR target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [9, 5] x `long_len` [21, 50] x `rr` [2.0, 1.0]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- No stop (as written); marketable targets closed one bar late. Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

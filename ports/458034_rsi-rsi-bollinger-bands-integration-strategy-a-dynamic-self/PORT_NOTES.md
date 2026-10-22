# #458034 RSI-布林通道整合策略动态自适应的多指标交易系统-RSI-Bollinger-Bands-Integration-Strategy-A-Dynamic-Self-Adaptive-Multi-Indicator-Trading-System -> `fmz_458034_bollinger_snapback_rsi9_dip_atr_bracket_long`

- FMZ source id: 458034 (lineage).
- Source: https://www.fmz.com/strategy/458034 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 14:00:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C199). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the signal-low levels as fractions; from flat in a loop |
| 2 | PASS | Band snap-backs with an RSI dip |
| 3 | PASS | No exchange named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_len` [30, 20] x `rsi_len` [9, 14] x `atr_mult` [2.0, 1.0]: **8 trials**; the 25 / 75 levels fixed.

## Ambiguities resolved

- No bar size (bar_size_pending); bracket from the signal low. Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`bar_size_pending`

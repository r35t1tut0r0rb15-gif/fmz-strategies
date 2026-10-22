# #477593 基于Z分数标准化的线性信号量化交易策略-Z-Score-Normalized-Linear-Signal-Quantitative-Trading-Strategy -> `fmz_477593_rsi_close_blend_zscore14_pct_bracket_reversal`

- FMZ source id: 477593 (lineage).
- Source: https://www.fmz.com/strategy/477593 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 16:14:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C235). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | Blended RSI / price z-score extremes with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [14, 50] x `threshold` [1.5, 2.0]: **4 trials**; alpha 0.5, target 2 %, stop 1 %.

## Ambiguities resolved

- Percent inputs used as fractions (2 % / 1 %), as written. Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "zscore_reversion"`.

## Marks

`trailing_stop_pending`

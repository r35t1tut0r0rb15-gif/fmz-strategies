# #474704 基于MACD与Supertrend的双重验证趋势跟踪交易策略-MACD-Supertrend-Dual-Confirmation-Trend-Following-Trading-Strategy -> `fmz_474704_macd_cross_custom_supertrend_stop_0p5_long`

- FMZ source id: 474704 (lineage).
- Source: https://www.fmz.com/strategy/474704 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 17:16:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C223). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | MACD cross-ups over a supertrend line with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [2, 3] x `atr_len` [20, 10]: **4 trials**; the bracket fixed.

## Ambiguities resolved

- Repeat-signal re-sends not followed (trailing_stop_pending). Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`

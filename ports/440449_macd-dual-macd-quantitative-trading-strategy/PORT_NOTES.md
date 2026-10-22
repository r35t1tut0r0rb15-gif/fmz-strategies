# #440449 基于双MACD量化交易策略Dual-MACD-Quantitative-Trading-Strategy -> `fmz_440449_dual_macd_weekly_window_long`

- FMZ source id: 440449 (lineage).
- Source: https://www.fmz.com/strategy/440449 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-30 16:43:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C134). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks; the low-based trail pending |
| 2 | PASS | Daily and weekly MACD crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 20 % of equity, capital and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.30, 0.10] x `sign_len` [9, 5]: **4 trials**; MACD 12 / 26 fixed.

## Ambiguities resolved

- Weekly MACD from the last completed broker week; low-based trail pending. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending, coarse_bar_stop`

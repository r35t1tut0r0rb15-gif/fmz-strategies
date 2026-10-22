# #474884 基于支撑位突破的动态ATR趋势跟踪策略-Dynamic-ATR-Trend-Following-Strategy-Based-on-Support-Breakout -> `fmz_474884_ema50_200_trend_outside_consolidation_reversal_bracket_pending`

- FMZ source id: 474884 (lineage).
- Source: https://www.fmz.com/strategy/474884 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 17:26:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C226). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA trend states with a consolidation filter; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-based lot size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_short` [50, 20] x `ema_long` [200, 100]: **4 trials**; the bracket pending.

## Ambiguities resolved

- Per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`

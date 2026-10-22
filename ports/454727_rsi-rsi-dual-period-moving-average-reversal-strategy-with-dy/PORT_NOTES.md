# #454727 RSI双周期均线反转策略与动态风险管理系统-RSI-Dual-Period-Moving-Average-Reversal-Strategy-with-Dynamic-Risk-Management-System -> `fmz_454727_rsi2_reversal_ema10_400_stop_reversal`

- FMZ source id: 454727 (lineage).
- Source: https://www.fmz.com/strategy/454727 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 14:01:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop as a fixed fraction; re-issued stops pending (mark) |
| 2 | PASS | RSI 2 reversals with EMA exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [400, 200] x `sl_pct` [0.01, 0.05]: **8 trials**; the RSI levels fixed.

## Ambiguities resolved

- Re-issued stops pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

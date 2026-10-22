# #473236 Multi Technical Indicator Trend Following Strategy with Ichimoku Cloud Breakout and Stop Loss System -> `fmz_473236_ichimoku_cloud_ma_weekly_rsi_kijun_exit_reversal`

- FMZ source id: 473236 (lineage).
- Source: https://www.fmz.com/strategy/473236 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:13:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C214). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly RSI from completed weeks |
| 2 | PASS | Ichimoku breakouts with MA and weekly RSI filters; moving cloud stop described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_ob` [70, 60] x `rsi_os` [30, 40]: **4 trials**; the Ichimoku and MA lengths fixed; the cloud stop pending.

## Ambiguities resolved

- Weekly RSI from the last completed broker week; cloud stop pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`trailing_stop_pending`

# #454146 G趋势EMA-ATR智能交易策略G-Trend-EMA-ATR-Intelligent-Trading-Strategy -> `fmz_454146_g_channel_trend_vs_ema50_state_reversal`

- FMZ source id: 454146 (lineage).
- Source: https://www.fmz.com/strategy/454146 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-06-14 15:35:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending (mark) |
| 2 | PASS | Channel trend against the EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [100, 50] x `ema_len` [50, 100]: **4 trials**.

## Ambiguities resolved

- The re-sent bracket pending. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`trailing_stop_pending`

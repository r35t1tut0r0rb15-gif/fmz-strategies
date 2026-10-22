# #489966 多指标协同动态风险管理短线交易策略EMAMACDRSI结合ATR自适应止损止盈技术-Multi-Indicator-Synergistic-Dynamic-Risk-Management-Scalping-Strategy-EMAMACDRSI-with-ATR-Adaptive-Stop-Loss-Take-Profit-Technique -> `fmz_489966_ema50_side_macd_hist_rsi_band_state_reversal_2d`

- FMZ source id: 489966 (lineage).
- Source: https://www.fmz.com/strategy/489966 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-10 15:27:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C272). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | EMA / MACD / RSI states |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`emaLength` [50, 100] x `rsiOB` [70, 80]: **4 trials** (oversold 100 minus it); MACD 12 / 26 / 9, RSI 14.

## Ambiguities resolved

- The per-bar bracket is pending. REVERSAL INTENDED. FREQ = "2D" (two broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`trailing_stop_pending`

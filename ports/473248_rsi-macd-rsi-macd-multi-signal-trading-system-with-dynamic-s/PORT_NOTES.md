# #473248 RSI-MACD多重信号交易系统结合动态止盈止损策略-RSI-MACD-Multi-Signal-Trading-System-with-Dynamic-Stop-Management -> `fmz_473248_macd6_13_7_cross_rsi_extremes_reversal`

- FMZ source id: 473248 (lineage).
- Source: https://www.fmz.com/strategy/473248 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-28 15:47:00). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C215). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD crossings at RSI extremes; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only (XAU/USD named in the title). |
| 4 | DONE | Fixed lot stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_os` [35, 30] x `rsi_ob` [70, 65]: **4 trials**; the MACD lengths fixed; the per-bar bracket pending.

## Ambiguities resolved

- Header's daily bars followed; per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`

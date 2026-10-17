# #489966 多指标协同动态风险管理短线交易策略EMAMACDRSI结合ATR自适应止损止盈技术-Multi-Indicator-Synergistic-Dynamic-Risk-Management-Scalping-Strategy-EMAMACDRSI-with-ATR-Adaptive-Stop-Loss-Take-Profit-Technique -> `fmz_489966_ema_macd_rsi_atr_bracket_2d`

- FMZ source id: 489966 (lineage).
- Source: https://www.fmz.com/strategy/489966 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-10 15:27:13). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket fixed at entry (mark). |
| 2 | PASS | EMA, MACD, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [1.0, 2.0] x `tp_atr` [2.0, 4.0]: **4 trials**; defaults 1 / 2 (the source's); EMA 50, MACD 12 / 26 / 9,
RSI 14 (70 / 30) and ATR 14 fixed.

## Moving bracket (rule 2, mark `trailing_stop_pending`)

As written the stop and target are re-computed every bar from the current close +- 1 / 2 ATR (`strategy.exit` with
`from_entry = ""`). The port fixes them at the signal bar (`sl_stop` / `tp_stop` from its ATR, re-based on the fill).

## Ambiguities resolved

- Two-day bars from broker days in fixed blocks counted from 1970-01-01 (block phase: decision owed), as #426509:
  `coarse_bar_stop`.
- Every condition bar is an entry; entries reverse. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`

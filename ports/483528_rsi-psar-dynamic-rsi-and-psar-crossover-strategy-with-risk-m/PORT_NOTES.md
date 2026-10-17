# #483528 动态RSI与PSAR交叉策略结合风险管理系统-Dynamic-RSI-and-PSAR-Crossover-Strategy-with-Risk-Management-System -> `fmz_483528_psar_cross_rsi_oversold_long_bracket`

- FMZ source id: 483528 (lineage).
- Source: https://www.fmz.com/strategy/483528 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 10:27:37). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Parabolic SAR, RSI and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_os` [30, 40] x `tp_pct` [5.0, 8.0]: **4 trials**; defaults 30 / 5 (the source's); SAR 0.02 / 0.02 / 0.2, RSI 14,
the 70 exit level and the 3 % stop fixed.

## Trailing stop (mark `trailing_stop_pending`)

A later buy signal while held re-places the stop and target from the new close. The port keeps the entry's bracket.

## Ambiguities resolved

- `ta.sar` as TradingView documents it (as #428699).
- Long only: opposite entries cannot occur. The sell close is an exit signal. Stop module: `portfolio_kwargs` {} (D4).
  FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`trailing_stop_pending`

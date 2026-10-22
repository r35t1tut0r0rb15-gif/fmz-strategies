# #454147 EMA-RSI-MACD动态止盈止损交易策略-EMA-RSI-MACD-Dynamic-Take-Profit-and-Stop-Loss-Trading-Strategy -> `fmz_454147_hlcc4_ema_cross_rsi_macd_tick_bracket_from_flat`

- FMZ source id: 454147 (lineage).
- Source: https://www.fmz.com/strategy/454147 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-14 15:38:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C194). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples |
| 2 | PASS | Multi-confirmed EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.001, 1.0] x `ema3_len` [34, 50]: **4 trials**; the EMA 9 / 21, RSI and MACD lengths fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples (1D ~1000). Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`

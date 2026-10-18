# #435775 基于MACD和RSI的趋势追踪反转策略MACD-and-RSI-Based-Trend-Following-Reversal-Strategy -> `fmz_435775_macd_ema_rsi_flags`

- FMZ source id: 435775 (lineage).
- Source: https://www.fmz.com/strategy/435775 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 17:53:38). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram, EMA trend and RSI limits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [200, 100] x `rsi_len` [14, 7]: **4 trials**; MACD 12 / 26 / 9 and the 70 / 30 limits fixed.

## Ambiguities resolved

- Script flags followed inside simulate; orders in call order. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`

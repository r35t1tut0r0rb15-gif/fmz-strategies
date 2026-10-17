# #483121 动态趋势动量交叉策略-基于双重EMA与MACD指标的量化交易系统-Dynamic-Trend-Momentum-Crossover-Strategy-Quantitative-Trading-System-Based-on-Dual-EMA-and-MACD-Indicators -> `fmz_483121_ema12_26_macd_side_pct_bracket`

- FMZ source id: 483121 (lineage).
- Source: https://www.fmz.com/strategy/483121 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:56:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages, MACD and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [2.0, 3.0] x `tp_pct` [5.0, 8.0]: **4 trials**; defaults 2 / 5 (the source's); EMA 12 / 26 and MACD
12 / 26 / 9 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A same-side signal while held re-places the stop and target from the new close. The port keeps the entry's bracket.

## Ambiguities resolved

- A short signal while long also meets the long exit: only the entry is emitted (a reversal); long side mirrored.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`

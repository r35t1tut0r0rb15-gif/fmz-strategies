# #483104 多重均线与RSI交叉动态ATR止盈止损策略-Multi-SMA-and-RSI-Crossover-Strategy-with-Dynamic-ATR-based-Take-Profit-and-Stop-Loss -> `fmz_483104_four_sma_band_cross_rsi7_atr_bracket`

- FMZ source id: 483104 (lineage).
- Source: https://www.fmz.com/strategy/483104 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:44:39). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | Moving averages of highs and lows, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 2.0] x `tp_mult` [2.5, 4.0]: **4 trials**; defaults 1.5 / 2.5 (the source's); SMA 20 / 50 bands,
RSI 7 / 50 and ATR 14 fixed.

## Trailing stop (mark `trailing_stop_pending`)

A buy signal while held re-issues the exit with the new ATR. The port keeps the entry's bracket.

## Ambiguities resolved

- `loss` / `profit` are ticks given ATR price distances: read as price distances (as #427592).
- All five crosses must fall on one bar, as written. Long only: opposite entries cannot occur.
- Stop module: `portfolio_kwargs` {} (D4). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`trailing_stop_pending`

# #483027 动态趋势RSI交叉动量增强策略-Dynamic-Trend-RSI-Crossover-Momentum-Enhancement-Strategy -> `fmz_483027_sma_atr_line_rsi_always_in`

- FMZ source id: 483027 (lineage).
- Source: https://www.fmz.com/strategy/483027 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 10:00:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR band around an SMA and RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_len` [10, 20]: **4 trials**; defaults 3 / 10 (the source's); RSI 14 (70 / 30) fixed.

## Ambiguities resolved

- The line is the source's own recursion (`close > nz(line[1], close) ? lower : upper`), not `ta.supertrend`.
- Every bar is an entry signal for its side: stop-and-reverse; with both conditions the later short wins.
- REVERSAL INTENDED; no exits or stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`

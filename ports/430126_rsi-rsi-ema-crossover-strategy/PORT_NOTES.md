# #430126 RSI均线交叉策略RSI-EMA-Crossover-Strategy -> `fmz_430126_ema_stack_rsi_band_long`

- FMZ source id: 430126 (lineage).
- Source: https://www.fmz.com/strategy/430126 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-25 11:46:49). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving averages and RSI levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [26, 14] x `m_line` [42, 50]: **4 trials**; EMA 17 / 35 / 142 and the upper line 70 fixed.

## Ambiguities resolved

- Entry and close on one bar: flat if already long, long if flat. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`

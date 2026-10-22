# #473709 RSI与Supertrend趋势跟踪型自适应波动策略-RSI-and-Supertrend-Trend-Following-Adaptive-Volatility-Strategy -> `fmz_473709_supertrend_2p76_atr12_flip_rsi_filter_reversal`

- FMZ source id: 473709 (lineage).
- Source: https://www.fmz.com/strategy/473709 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-02 16:41:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend flips with an RSI filter; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [2.76, 4.0] x `atr_period` [12, 24]: **4 trials**; the bracket pending.

## Ambiguities resolved

- Per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "3D" (blocks of 3 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`trailing_stop_pending`

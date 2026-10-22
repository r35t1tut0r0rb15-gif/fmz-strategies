# #454742 SuperTrend策略优化动态波动率跟踪与交易信号增强系统-SuperTrend-Strategy-Optimization-Dynamic-Volatility-Tracking-and-Enhanced-Trading-Signal-System -> `fmz_454742_classic_supertrend_flip_reversal`

- FMZ source id: 454742 (lineage).
- Source: https://www.fmz.com/strategy/454742 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-06-21 15:30:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Supertrend flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427399. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_len` [10, 14] x `mult` [3.0, 2.0]: **4 trials**.

## Ambiguities resolved

- Date window dropped. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`

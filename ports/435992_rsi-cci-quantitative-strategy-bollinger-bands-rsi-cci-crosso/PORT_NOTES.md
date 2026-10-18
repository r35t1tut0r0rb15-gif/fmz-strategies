# #435992 布林带RSI指标的CCI均线交叉策略Quantitative-Strategy-Bollinger-Bands-RSI-CCI-Crossover-Strategy -> `fmz_435992_bollinger_rsi_cci_extremes_tp`

- FMZ source id: 435992 (lineage).
- Source: https://www.fmz.com/strategy/435992 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 16:24:49). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry |
| 2 | ADAPT | Tick target -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick take-profit input quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.2, 1.0] x `length` [20, 30]: **4 trials**; RSI 14 at 33 / 70 and the CCI levels fixed.

## Ambiguities resolved

- Tick target -> ATR multiple; no stop. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`

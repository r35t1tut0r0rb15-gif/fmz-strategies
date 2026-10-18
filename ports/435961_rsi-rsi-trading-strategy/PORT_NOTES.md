# #435961 基于相对强弱指标RSI交易策略RSI-Trading-Strategy -> `fmz_435961_rsi_30_70_cross_reversal`

- FMZ source id: 435961 (lineage).
- Source: https://www.fmz.com/strategy/435961 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 14:20:26). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI band crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The initial capital input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `oversold` [30, 20]: **4 trials**; the overbought level is 100 minus the oversold level.

## Ambiguities resolved

- Explicit closes equal the reversal. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`

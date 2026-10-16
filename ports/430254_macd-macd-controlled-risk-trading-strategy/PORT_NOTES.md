# #430254 基于MACD指标的止损策略MACD-Controlled-Risk-Trading-Strategy -> `fmz_430254_macd_below_zero_wma_bracket_long`

- FMZ source id: 430254 (lineage).
- Source: https://www.fmz.com/strategy/430254 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-26 15:51:34). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | MACD signs, a moving average and a risk-multiple target. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 1 % risk sizing stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`wma_length` [150, 100] x `r_exit` [4.0, 2.0]: **4 trials**; MACD 12 / 26 / 9, 5-bar window and the 3-bar low fixed.

## Ambiguities resolved

- Flat follows the house bracket on bars. Mark coarse_bar_stop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`

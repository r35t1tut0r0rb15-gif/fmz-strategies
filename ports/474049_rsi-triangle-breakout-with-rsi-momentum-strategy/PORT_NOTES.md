# #474049 三角形突破结合RSI动量策略-Triangle-Breakout-with-RSI-Momentum-Strategy -> `fmz_474049_linreg15_high_low_break_rsi50_reversal`

- FMZ source id: 474049 (lineage).
- Source: https://www.fmz.com/strategy/474049 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-05 16:19:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C220). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Regression-line breakouts with an RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [15, 30] x `rsi_buy` [50, 60]: **4 trials**; the sell level 50.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`

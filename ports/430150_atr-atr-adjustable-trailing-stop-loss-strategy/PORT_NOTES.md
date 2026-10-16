# #430150 ATR可调节跟踪止损策略ATR-Adjustable-Trailing-Stop-Loss-Strategy -> `fmz_430150_atr_trailing_line_cross`

- FMZ source id: 430150 (lineage).
- Source: https://www.fmz.com/strategy/430150 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-25 15:08:04). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C33). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR line. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hhv` [10, 20] x `mult` [2.5, 3.5]: **4 trials**; ATR 5 fixed.

## Ambiguities resolved

- TS is highest(high - mult x ATR, hhv) only. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
